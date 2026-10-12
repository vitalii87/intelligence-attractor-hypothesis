"""Yield/resume protocol for package-authored prompts within one iteration."""
from dataclasses import replace
import json
from pathlib import Path
import time

from .agent_package import run_package
from .model_gateway import GatewayError


def run_dialogue(directory, runtime, limits, task_text, gateway, *, max_launches=16):
    if type(max_launches) is not int or not 1 <= max_launches <= 256:
        raise ValueError("max_launches must be in [1, 256]")
    # Gateway journal is controller-owned and must never be candidate-mounted.
    if gateway.path.resolve().is_relative_to(Path(directory).resolve()):
        raise ValueError("gateway journal must be outside candidate workspace")
    reply = None
    first = None
    launches = []
    started = time.monotonic()
    for index in range(max_launches):
        remaining = limits.timeout_seconds - (time.monotonic() - started)
        if remaining <= 0:
            raise GatewayError("iteration wall-time allowance exhausted")
        context = {**gateway.status(), "reply": reply,
                   "protocol": {"request": {"action": "model", "request": {"id": "unique string", "prompt": "your text", "max_output_tokens": "integer"}},
                                "finish": {"action": "complete"}},
                   "launches_remaining": max_launches - index}
        report = run_package(directory, runtime, replace(limits, timeout_seconds=remaining),
                             task_text, model_context=context)
        first = first or report["before"]
        launches.append({"before_sha256": report["before"]["sha256"], "runtime": report["runtime"]})
        execution = report["runtime"]
        if not report["package_valid"] or execution["exit_code"] != 0 or execution["timed_out"] or execution["output_truncated"]:
            raise GatewayError("package execution failed during dialogue")
        if time.monotonic() - started >= limits.timeout_seconds:
            raise GatewayError("iteration wall-time allowance exhausted")
        try:
            action = json.loads(execution["stdout"])
        except (ValueError, RecursionError):
            raise GatewayError("stdout must contain one JSON action") from None
        if not isinstance(action, dict):
            raise GatewayError("invalid package action")
        if action == {"action": "complete"}:
            return {**report, "before": first,
                    "changed": first["sha256"] != report["after"]["sha256"],
                    "launches": launches, "gateway": gateway.status()}
        if set(action) != {"action", "request"} or action["action"] != "model":
            raise GatewayError("invalid package action")
        if index + 1 == max_launches:
            raise GatewayError("no launch allowance to deliver a model response")
        reply = {"id": action["request"].get("id") if isinstance(action["request"], dict) else None,
                 **gateway.request(action["request"])}
    raise GatewayError("launch allowance exhausted")
