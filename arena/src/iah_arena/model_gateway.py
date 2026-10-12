"""Provider-neutral durable token gate. Backends are trusted controller code."""
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path

from .locking import FileLock


class GatewayError(RuntimeError):
    pass


@dataclass(frozen=True)
class GatewayLimits:
    calls: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    request_input_tokens: int
    request_output_tokens: int
    max_prompt_chars: int = 30000

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in asdict(self).values()):
            raise ValueError("gateway limits must be positive integers")


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def _save(path, state):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump({"state": state, "sha256": _hash(state)}, stream, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


class ModelGateway:
    """One journal per iteration, outside all candidate mounts.

    backend.count(prompt) returns input tokens; backend.generate(prompt, max_output)
    returns {text, input_tokens, output_tokens}. Model/backend identity is frozen
    by backend_id supplied by the controller. No API keys enter this protocol.
    """
    def __init__(self, path: Path, limits: GatewayLimits, backend, *, backend_id: str):
        if not isinstance(backend_id, str) or not backend_id:
            raise ValueError("backend identity required")
        self.path, self.limits, self.backend = Path(path), limits, backend
        self.backend_id = backend_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = self.path.with_suffix(".lock")
        with FileLock(self.lock):
            if not self.path.exists():
                _save(self.path, {"limits": asdict(limits), "backend_id": backend_id,
                                  "usage": {"calls": 0, "input_tokens": 0, "output_tokens": 0}, "requests": {}})
            self._read()

    def _read(self):
        envelope = json.loads(self.path.read_text(encoding="utf-8"))
        state = envelope["state"]
        if envelope["sha256"] != _hash(state):
            raise GatewayError("gateway journal checksum mismatch")
        if state["limits"] != asdict(self.limits) or state["backend_id"] != self.backend_id:
            raise GatewayError("gateway settings changed")
        return state

    def status(self):
        with FileLock(self.lock):
            state = self._read()
            usage = state["usage"]
            return {"backend_id": self.backend_id, "limits": asdict(self.limits),
                    "usage": {**usage, "total_tokens": usage["input_tokens"] + usage["output_tokens"]}}

    def request(self, request):
        if not isinstance(request, dict) or set(request) != {"id", "prompt", "max_output_tokens"}:
            raise GatewayError("invalid model request fields")
        identifier, prompt, output = request["id"], request["prompt"], request["max_output_tokens"]
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
            raise GatewayError("invalid request ID")
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > self.limits.max_prompt_chars:
            raise GatewayError("invalid prompt length")
        if type(output) is not int or not 1 <= output <= self.limits.request_output_tokens:
            raise GatewayError("invalid output reservation")
        fingerprint = _hash(request)
        with FileLock(self.lock):
            state = self._read()
            previous = state["requests"].get(identifier)
            if previous:
                if previous["sha256"] != fingerprint:
                    raise GatewayError("request ID reused with different content")
                if previous["status"] != "completed":
                    raise GatewayError("uncertain request cannot be replayed; reservation retained")
                return previous["response"]
            usage = state["usage"]
            cap = self.limits.request_input_tokens
            projected_in, projected_out = usage["input_tokens"] + cap, usage["output_tokens"] + output
            if (usage["calls"] >= self.limits.calls or projected_in > self.limits.input_tokens or
                projected_out > self.limits.output_tokens or projected_in + projected_out > self.limits.total_tokens):
                raise GatewayError("iteration model budget exhausted")
            try:
                count = self.backend.count(prompt)
            except Exception:
                raise GatewayError("input counting failed; generation not sent") from None
            if type(count) is not int or not 0 <= count <= cap:
                raise GatewayError("input exceeds request cap or invalid token count")
            usage.update(calls=usage["calls"] + 1, input_tokens=projected_in, output_tokens=projected_out)
            record = {"sha256": fingerprint, "status": "reserved", "request": request}
            state["requests"][identifier] = record
            _save(self.path, state)  # A crash from this point never erases expenditure.
            try:
                response = self.backend.generate(prompt, output)
                if not isinstance(response, dict) or set(response) != {"text", "input_tokens", "output_tokens"}:
                    raise ValueError("invalid response")
                if not isinstance(response["text"], str) or len(response["text"]) > 1000000:
                    raise ValueError("invalid text")
                if any(type(response[k]) is not int or not 0 <= response[k] <= bound
                       for k, bound in (("input_tokens", cap), ("output_tokens", output))):
                    raise ValueError("invalid usage")
            except Exception:
                raise GatewayError("generation failed or usage invalid; reservation retained") from None
            usage["input_tokens"] -= cap - response["input_tokens"]
            usage["output_tokens"] -= output - response["output_tokens"]
            record.update(status="completed", response=response)
            _save(self.path, state)
            return response
