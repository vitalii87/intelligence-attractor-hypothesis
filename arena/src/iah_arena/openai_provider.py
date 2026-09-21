"""Stateless Responses API adapter. No retries, SDK, or candidate-side secrets."""
from __future__ import annotations

import json
import os
import urllib.request

from .budgets import BudgetDelta, BudgetExceeded
from .providers import ProviderTurn, ToolCall


class ProviderError(RuntimeError):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OpenAITransport:
    def __init__(self, key_env, timeout):
        self.key = os.environ.get(key_env, "")
        if not self.key:
            raise ValueError(f"missing API credential environment variable: {key_env}")
        self.timeout = timeout

    def __call__(self, route, payload):
        request = urllib.request.Request(
            "https://api.openai.com/v1/" + route,
            data=json.dumps(payload, allow_nan=False).encode(),
            headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.build_opener(_NoRedirect()).open(request, timeout=self.timeout) as response:
                raw = response.read(8_000_001)
                if len(raw) > 8_000_000:
                    raise ValueError("response too large")
                return json.loads(raw)
        except Exception:
            # Do not persist response bodies, request headers, or credentials.
            raise ProviderError("OpenAI request failed; no automatic retry") from None


def _integer(value):
    if type(value) is not int or value < 0:
        raise ProviderError("invalid token usage")
    return value


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, model, settings, budget, transport=None):
        self.model_id, self.settings, self.budget = model, settings, budget
        self.transport = transport or OpenAITransport(settings["key_env"], settings["timeout_seconds"])
        self.history = []
        self.last_id = None
        self.pending = set()

    def start(self, context, tools):
        if self.history:
            raise ProviderError("provider instance cannot be shared between attempts")
        if not context.prompt_text:
            raise ProviderError("bounded decision prompt required")
        self.history = [{"role": "user", "content": context.prompt_text}]
        return self._request(tools)

    def continue_with_results(self, provider_response_id, results, tools):
        if provider_response_id != self.last_id or not self.pending:
            raise ProviderError("invalid continuation")
        if len(results) != len(self.pending) or {r.call_id for r in results} != self.pending:
            raise ProviderError("tool results do not match pending calls")
        self.history.extend({"type": "function_call_output", "call_id": r.call_id,
                             "output": json.dumps({"is_error": r.is_error, "output": dict(r.output)})}
                            for r in results)
        return self._request(tools)

    def _cost(self, inputs, outputs):
        # Rates are integer micro-USD per million tokens. Ignore cache discounts.
        return (inputs * self.settings["input_microusd_per_million"] +
                outputs * self.settings["output_microusd_per_million"] + 999_999) // 1_000_000

    def _request(self, tools):
        if not self.budget.can_charge(BudgetDelta(model_calls=1)):
            raise BudgetExceeded("model call budget reached")
        base = {"model": self.model_id, "input": self.history,
                "tools": [{"type": "function", "name": t.name, "description": t.description,
                           "parameters": dict(t.input_schema), "strict": False} for t in tools]}
        count = self.transport("responses/input_tokens", base)
        inputs = _integer(count.get("input_tokens"))
        cap = self.settings["max_input_tokens"]
        outputs = self.settings["max_output_tokens"]
        if inputs > cap:
            raise BudgetExceeded("request input token cap exceeded")
        reservation = BudgetDelta(model_calls=1, input_tokens=cap, output_tokens=outputs,
                                  cost_microusd=self._cost(cap, outputs))
        if not self.budget.can_charge(reservation):
            raise BudgetExceeded("insufficient budget for full API request reservation")
        try:
            response = self.transport("responses", {**base, "store": False,
                "include": ["reasoning.encrypted_content"], "parallel_tool_calls": False,
                "max_output_tokens": outputs})
            usage = response["usage"]
            actual_in = _integer(usage["input_tokens"])
            actual_out = _integer(usage["output_tokens"])
            if actual_in > cap or actual_out > outputs:
                raise ProviderError("API usage exceeded configured request reservation")
            if response["status"] != "completed":
                raise ProviderError("API response was not completed")
            response_id = response["id"]
            if not isinstance(response_id, str) or not response_id:
                raise ProviderError("missing response ID")
            calls, texts = [], []
            allowed = {t.name for t in tools}
            for item in response["output"]:
                if item["type"] == "function_call":
                    arguments = json.loads(item["arguments"])
                    call_id = item["call_id"]
                    if not isinstance(arguments, dict) or item["name"] not in allowed or not isinstance(call_id, str) or not call_id:
                        raise ProviderError("invalid function call")
                    calls.append(ToolCall(call_id, item["name"], arguments))
                elif item["type"] == "message":
                    texts.extend(c["text"] for c in item["content"] if c["type"] == "output_text")
                elif item["type"] != "reasoning":
                    raise ProviderError("unexpected API output type")
            if len({c.call_id for c in calls}) != len(calls):
                raise ProviderError("duplicate function call IDs")
            self.history.extend(response["output"])
            self.last_id = response_id
            self.pending = {c.call_id for c in calls}
            return ProviderTurn(tuple(calls), "\n".join(texts) or None, response_id,
                                {"input_tokens": actual_in, "output_tokens": actual_out,
                                 "cost_microusd": self._cost(actual_in, actual_out)})
        except Exception:
            # Success is charged by DecisionSessionRunner; uncertain calls retain
            # a full reservation here. Abrupt process death retains the attempt.
            self.budget.charge(reservation)
            raise ProviderError("OpenAI generation failed or invalid; full request reservation retained") from None
