import copy
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iah_arena.budgets import BudgetDelta, BudgetExceeded, BudgetLedger, BudgetLimits
from iah_arena.iteration_config import load_config, validate_config
from iah_arena.openai_provider import OpenAIProvider, OpenAITransport, ProviderError
from iah_arena.providers import DecisionContext, ToolResult
from iah_arena.tools import CANONICAL_TOOLS
from iah_arena.iterations import create_iterations, continue_iterations
from iah_arena.tasks.integer_sum import SEEDS, SOLUTIONS
from test_iterations import FixtureRuntime

SETTINGS = dict(key_env="ARENA_TEST_KEY", timeout_seconds=30, max_input_tokens=1000,
                max_output_tokens=100, input_microusd_per_million=1_000_000,
                output_microusd_per_million=2_000_000)


def response(output=None):
    return {"id": "resp-1", "status": "completed", "usage": {"input_tokens": 20, "output_tokens": 5},
            "output": output if output is not None else [
                {"type": "function_call", "call_id": "call-1", "name": "read_file",
                 "arguments": json.dumps({"path": "solver.py"})}]}


class Transport:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def __call__(self, route, payload):
        self.requests.append((route, copy.deepcopy(payload)))
        item = next(self.replies)
        if isinstance(item, Exception):
            raise item
        return item


class OpenAITests(unittest.TestCase):
    def setUp(self):
        self.budget = BudgetLedger(BudgetLimits(4, 4000, 400, 4800, 0))
        self.context = DecisionContext("a", 1, 0, 1, {}, {}, {}, {}, prompt_text="Improve solver")

    def provider(self, replies):
        self.transport = Transport(replies)
        return OpenAIProvider("test-model", SETTINGS, self.budget, self.transport)

    def test_function_roundtrip_stateless_history_and_actual_usage(self):
        final = response([{"type": "message", "content": [{"type": "output_text", "text": "done"}]}])
        provider = self.provider([{"input_tokens": 20}, response(), {"input_tokens": 40}, final])
        turn = provider.start(self.context, CANONICAL_TOOLS)
        self.assertEqual(turn.tool_calls[0].arguments, {"path": "solver.py"})
        self.assertEqual(turn.usage["cost_microusd"], 30)
        # Session runner owns successful-turn accounting.
        self.budget.charge(BudgetDelta(model_calls=1, **turn.usage))
        result = provider.continue_with_results("resp-1", [ToolResult("call-1", {"content": "x"})], CANONICAL_TOOLS)
        self.assertEqual(result.final_text, "done")
        payload = self.transport.requests[-1][1]
        self.assertFalse(payload["store"])
        self.assertFalse(payload["parallel_tool_calls"])
        self.assertNotIn("previous_response_id", payload)
        self.assertEqual(payload["input"][-1]["type"], "function_call_output")
        self.assertEqual(payload["input"][-2]["type"], "function_call")
        self.assertEqual(self.budget.usage.model_calls, 1)
        with self.assertRaises(ProviderError):
            provider.start(self.context, CANONICAL_TOOLS)

    def test_preflight_blocks_generation(self):
        provider = self.provider([{"input_tokens": 1001}])
        with self.assertRaises(BudgetExceeded):
            provider.start(self.context, CANONICAL_TOOLS)
        self.assertEqual(len(self.transport.requests), 1)
        self.assertEqual(self.budget.usage.model_calls, 0)

    def test_insufficient_money_blocks_generation(self):
        self.budget = BudgetLedger(BudgetLimits(4, 4000, 400, 100, 0))
        provider = self.provider([{"input_tokens": 20}])
        with self.assertRaises(BudgetExceeded):
            provider.start(self.context, CANONICAL_TOOLS)
        self.assertEqual(len(self.transport.requests), 1)

    def test_timeout_and_invalid_responses_keep_reservation_without_retry(self):
        malformed = response()
        malformed["output"][0]["arguments"] = "not-json"
        missing = response()
        del missing["usage"]
        incomplete = response()
        incomplete["status"] = "incomplete"
        for reply in [TimeoutError("secret"), malformed, missing, incomplete]:
            with self.subTest(reply=type(reply)):
                self.setUp()
                provider = self.provider([{"input_tokens": 20}, reply])
                with self.assertRaisesRegex(ProviderError, "reservation retained") as error:
                    provider.start(self.context, CANONICAL_TOOLS)
                self.assertNotIn("secret", str(error.exception))
                self.assertEqual(self.budget.usage.input_tokens, 1000)
                self.assertEqual(self.budget.usage.output_tokens, 100)
                self.assertEqual(self.budget.usage.cost_microusd, 1200)
                self.assertEqual(self.budget.usage.model_calls, 1)
                self.assertEqual(len(self.transport.requests), 2)

    def test_tool_result_identity_and_independent_instances(self):
        provider = self.provider([{"input_tokens": 20}, response()])
        provider.start(self.context, CANONICAL_TOOLS)
        with self.assertRaises(ProviderError):
            provider.continue_with_results("wrong", [ToolResult("call-1", {})], CANONICAL_TOOLS)
        with self.assertRaises(ProviderError):
            provider.continue_with_results("resp-1", [ToolResult("wrong", {})], CANONICAL_TOOLS)
        other = OpenAIProvider("test-model", SETTINGS, self.budget, Transport([]))
        self.assertEqual(other.history, [])

    def test_transport_redacts_errors(self):
        with patch.dict("os.environ", {"ARENA_TEST_KEY": "secret-token"}):
            transport = OpenAITransport("ARENA_TEST_KEY", 10)
        with patch("urllib.request.OpenerDirector.open", side_effect=ValueError("secret-token")):
            with self.assertRaises(ProviderError) as error:
                transport("responses", {})
        self.assertNotIn("secret-token", str(error.exception))

    def test_config_requires_docker_rates_and_budget(self):
        config = load_config(Path(__file__).resolve().parents[1] / "iteration.example.toml")
        config["lineages"][0]["model"] = "openai/test-model"
        with self.assertRaises(ValueError):
            validate_config(config)
        config["openai"] = SETTINGS.copy()
        config["runtime"].update(engine="docker", image="python@sha256:" + "a" * 64)
        for section in ("total", "attempt"):
            config[section].update(input_tokens=4000, output_tokens=400, cost_microusd=4800)
        validate_config(config)
        config["openai"]["api_key"] = "must-not-be-saved"
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_full_iteration_with_mock_api_and_shared_accounting(self):
        example = Path(__file__).resolve().parents[1] / "iteration.example.toml"
        raw = example.read_text().replace('model = "scripted-v1"', 'model = "openai/test-model"')
        raw = raw.replace('engine = "trusted-local"', 'engine = "docker"').replace('image = ""', 'image = "python@sha256:' + 'a' * 64 + '"')
        for key, value in [("input_tokens", 4000), ("output_tokens", 400), ("cost_microusd", 4800)]:
            raw = raw.replace(f"{key} = 0", f"{key} = {value}")
        raw += "\n[openai]\n" + "\n".join(f"{k} = {json.dumps(v)}" for k, v in SETTINGS.items())
        claim = dict(bottleneck="negatives", hypothesis="sum all", changes=["sum"], expected_effect="correct", risks=["test"])
        calls = [("read_file", {"path": "solver.py"}),
                 ("write_file", {"path": "solver.py", "content": SOLUTIONS["loop"],
                                  "expected_sha256": hashlib.sha256(SEEDS["loop"].encode()).hexdigest()}),
                 ("run_public_tests", {}), ("submit_candidate", {"claim": claim})]
        replies = []
        for name, args in calls:
            replies.extend([{"input_tokens": 20}, response([{"type": "function_call", "call_id": name,
                                                            "name": name, "arguments": json.dumps(args)}])])
        transport = Transport(replies)
        with tempfile.TemporaryDirectory() as temporary, patch.dict("os.environ", {"ARENA_TEST_KEY": "fake"}), \
             patch("iah_arena.iterations._runtime", return_value=FixtureRuntime()), \
             patch("iah_arena.openai_provider.OpenAITransport", return_value=transport):
            config = Path(temporary) / "config.toml"
            config.write_text(raw)
            run = Path(temporary) / "run"
            create_iterations(config, run)
            state = continue_iterations(run, steps=1, progress=lambda _: None)
            self.assertEqual(state["history"][0]["status"], "accepted")
            usage = state["lineages"]["lineage-a"]["usage"]
            self.assertEqual(usage["model_calls"], 4)
            self.assertEqual(usage["cost_microusd"], 120)
            self.assertEqual(usage["input_tokens"], 80)
            self.assertNotIn("fake", (run / "iteration-state.json").read_text())
