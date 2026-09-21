"""Read-only local readiness report; never contacts a model provider."""
import hashlib
import os
from pathlib import Path

from . import __version__
from .docker_runtime import DockerRuntime, DockerRuntimeError
from .iteration_config import load_config


def check_iterations(config_path: Path) -> dict:
    report = {"arena_version": __version__, "ready": False, "scope": "local prerequisites only",
              "provider_contacted": False, "checks": [], "warnings": []}
    try:
        config = load_config(config_path)
    except (OSError, ValueError, TypeError) as error:
        # Invalid configuration may contain secrets accidentally pasted into keys.
        report["checks"].append({"name": "configuration", "ok": False,
                                 "detail": f"Invalid or unreadable TOML configuration ({type(error).__name__}); review the documented schema."})
        return report
    report["config_sha256"] = hashlib.sha256(Path(config_path).read_bytes()).hexdigest()
    report["checks"].append({"name": "configuration", "ok": True})
    real = [item for item in config["lineages"] if item["model"].startswith("openai/")]
    report["lineages"] = [{"id": item["id"], "origin": item["origin"], "model": item["model"]}
                           for item in config["lineages"]]
    report["limits"] = {
        "per_lineage_total": config["total"], "per_attempt_reservation": config["attempt"],
        "runtime": config["runtime"], "max_epochs": config["run"]["max_epochs"],
        "aggregate_configured_cost_microusd": len(real) * config["total"]["cost_microusd"],
        "max_generation_calls_per_lineage": min(config["total"]["model_calls"],
            config["run"]["max_epochs"] * config["attempt"]["model_calls"]),
    }
    if real:
        settings = config["openai"]
        present = bool(os.environ.get(settings["key_env"], ""))
        report["checks"].append({"name": "credential_present", "ok": present,
                                 "variable": settings["key_env"], "validity_verified": False})
        request_cost = (settings["max_input_tokens"] * settings["input_microusd_per_million"] +
                        settings["max_output_tokens"] * settings["output_microusd_per_million"] + 999_999) // 1_000_000
        report["limits"]["full_request_cost_microusd"] = request_cost
        report["limits"]["full_requests_fitting_attempt"] = min(
            config["attempt"]["model_calls"],
            config["attempt"]["input_tokens"] // settings["max_input_tokens"],
            config["attempt"]["output_tokens"] // settings["max_output_tokens"],
            config["attempt"]["cost_microusd"] // request_cost,
        )
        report["warnings"].append("Credential validity, model access, API compatibility and current prices are unverified; no provider request was sent.")
        report["warnings"].append("Cost limits use configured prices, not an invoice or provider-enforced spending limit.")
    runtime = config["runtime"]
    if runtime["engine"] == "docker":
        try:
            DockerRuntime(runtime["image"]).check_ready()
        except (DockerRuntimeError, OSError, ValueError):
            report["checks"].append({"name": "runtime", "ok": False,
                                     "detail": "Linux Docker engine or pinned local image unavailable. No image was pulled."})
        else:
            report["checks"].append({"name": "runtime", "ok": True,
                                     "detail": "Linux engine and local image found; container execution not tested."})
    else:
        report["checks"].append({"name": "runtime", "ok": True,
                                 "detail": "Bundled trusted fixtures only; no container isolation."})
    report["warnings"].append("integer-sum is a public integration task, not a validated scientific experiment.")
    report["ready"] = all(check["ok"] for check in report["checks"])
    return report
