import json
from pathlib import Path
import tempfile
import unittest

from iah_arena.model_gateway import GatewayError, GatewayLimits, ModelGateway
from iah_arena.package_attempts import PackageAttempts
from iah_arena.runtime import RuntimeLimits, RuntimeResult


class Backend:
    def __init__(self):
        self.prompts = []
        self.fail = False

    def count(self, prompt):
        return 5

    def generate(self, prompt, max_output):
        self.prompts.append(prompt)
        if self.fail:
            raise TimeoutError("secret")
        return {"text": "response", "input_tokens": 5, "output_tokens": 3}


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "gateway.json"
        self.backend = Backend()
        self.limits = GatewayLimits(3, 60, 30, 60, 20, 10)
        self.gateway = ModelGateway(self.path, self.limits, self.backend, backend_id="fake-v1")
        self.request = {"id": "one", "prompt": "My own instructions", "max_output_tokens": 10}

    def tearDown(self):
        self.tmp.cleanup()

    def test_exact_prompt_usage_and_durable_dedup(self):
        answer = self.gateway.request(self.request)
        restored = ModelGateway(self.path, self.limits, self.backend, backend_id="fake-v1")
        self.assertEqual(restored.request(self.request), answer)
        self.assertEqual(self.backend.prompts, [self.request["prompt"]])
        self.assertEqual(restored.status()["usage"]["total_tokens"], 8)
        with self.assertRaises(GatewayError):
            restored.request({**self.request, "prompt": "different"})

    def test_uncertainty_keeps_reservation_across_restart(self):
        self.backend.fail = True
        with self.assertRaises(GatewayError) as error:
            self.gateway.request(self.request)
        self.assertNotIn("secret", str(error.exception))
        restored = ModelGateway(self.path, self.limits, self.backend, backend_id="fake-v1")
        self.assertEqual(restored.status()["usage"]["total_tokens"], 30)
        with self.assertRaises(GatewayError):
            restored.request(self.request)
        self.assertEqual(len(self.backend.prompts), 1)

    def test_combined_limit_blocks_even_with_individual_allowances(self):
        limited = ModelGateway(self.path.parent / "other.json", GatewayLimits(3, 60, 30, 35, 20, 10), self.backend, backend_id="fake")
        limited.request(self.request)
        with self.assertRaisesRegex(GatewayError, "budget"):
            limited.request({**self.request, "id": "two"})
        self.assertEqual(len(self.backend.prompts), 1)

    def test_settings_tampering_and_invalid_requests(self):
        with self.assertRaises(GatewayError):
            ModelGateway(self.path, self.limits, self.backend, backend_id="changed")
        for request in ({}, {**self.request, "max_output_tokens": True}, {**self.request, "prompt": ""}):
            with self.assertRaises(GatewayError):
                self.gateway.request(request)
        value = json.loads(self.path.read_text())
        value["state"]["usage"]["calls"] = 100
        self.path.write_text(json.dumps(value))
        with self.assertRaises(GatewayError):
            self.gateway.status()

    def test_interruption_retains_reservation(self):
        def interrupt(*args):
            raise KeyboardInterrupt()
        self.backend.generate = interrupt
        with self.assertRaises(KeyboardInterrupt):
            self.gateway.request(self.request)
        self.assertEqual(self.gateway.status()["usage"]["total_tokens"], 30)

    def test_invalid_backend_usage_retains_full_reservation(self):
        self.backend.generate = lambda *args: {"text": "bad", "input_tokens": 21, "output_tokens": 1}
        with self.assertRaises(GatewayError):
            self.gateway.request(self.request)
        self.assertEqual(self.gateway.status()["usage"]["total_tokens"], 30)

    def test_input_cap_blocks_generation(self):
        self.backend.count = lambda _: 21
        with self.assertRaises(GatewayError):
            self.gateway.request(self.request)
        self.assertEqual(self.backend.prompts, [])
        self.assertEqual(self.gateway.status()["usage"]["calls"], 0)

    def test_package_controls_prompts_and_consumes_shared_budget(self):
        seen = []
        class Runtime:
            def run(inner, workspace, request, limits):
                passport = json.loads((request.extra_mounts[0].host_path / "context.json").read_text())
                seen.append(passport)
                reply = passport["model_gateway"]["reply"]
                if reply is None:
                    (workspace / "memory").write_text("waiting")
                    action = {"action": "model", "request": self.request}
                else:
                    self.assertEqual(reply["text"], "response")
                    (workspace / "memory").write_text(reply["text"])
                    action = {"action": "complete"}
                return RuntimeResult(0, False, 1, json.dumps(action))
        seed = self.path.parent / "seed"
        seed.mkdir()
        (seed / "agent.json").write_text('{"schema_version":1,"argv":["python3","agent.py"]}')
        (seed / "agent.py").write_text("pass")
        controller = PackageAttempts(self.path.parent / "state", "a")
        controller.initialize(seed)
        result = controller.run(epoch=1, attempt=1, runtime=Runtime(), limits=RuntimeLimits(1, 128, 32, 10),
                                task_text="Task", evaluator=lambda _: {"accepted": True, "reason": "fixture"},
                                gateway_limits=self.limits, backend=self.backend, backend_id="fake-v1")
        self.assertTrue(result["accepted"])
        self.assertEqual(result["package"]["gateway"]["usage"]["total_tokens"], 8)
        self.assertEqual(len(seen), 2)
        self.assertEqual((controller.manager.current_files() / "memory").read_text(), "response")
        self.assertFalse((controller.manager.current_files() / "gateway.json").exists())
