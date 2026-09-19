"""Strict, editable settings for exploratory iterative runs (not preregistration)."""
import math
import re
import tomllib
from pathlib import Path

from .docker_runtime import DockerRuntime
from .run_config import _exact_keys

BUDGET_FIELDS = {
    "model_calls", "input_tokens", "output_tokens", "cost_microusd",
    "compute_seconds", "edit_bytes", "edit_operations",
}


def validate_config(value: dict) -> dict:
    schemas = {
        "run": {"max_epochs", "min_attempts", "plateau_patience", "failure_limit", "max_tool_calls"},
        "total": BUDGET_FIELDS, "attempt": BUDGET_FIELDS,
        "runtime": {"engine", "image", "cpus", "memory_mb", "pids", "timeout_seconds", "tmpfs_mb", "max_output_bytes"},
        "task": {"id", "minimum_improvement", "development_cases", "selection_cases"},
        "workspace": {"max_file_bytes", "max_workspace_bytes"},
        "information": {"max_prompt_chars", "max_history_items", "max_metric_items", "max_workspace_files", "max_workspace_bytes"},
    }
    _exact_keys(value, required={"schema_version", "lineages", *schemas}, scope="iteration config")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported iteration config schema")
    for name, keys in schemas.items():
        if not isinstance(value[name], dict):
            raise ValueError(f"{name} must be a table")
        _exact_keys(value[name], required=keys, scope=name)
    for name in ("run", "total", "attempt", "workspace", "information"):
        for key, number in value[name].items():
            minimum = 1 if name in ("run", "workspace") else 0
            if type(number) is not int or number < minimum:
                raise ValueError(f"{name}.{key} must be an integer >= {minimum}")
    if value["run"]["min_attempts"] > value["run"]["max_epochs"]:
        raise ValueError("min_attempts exceeds max_epochs")
    if value["attempt"]["model_calls"] < 1 or value["attempt"]["compute_seconds"] < 1:
        raise ValueError("attempt model_calls and compute_seconds must be positive")
    for key in BUDGET_FIELDS:
        if value["attempt"][key] > value["total"][key]:
            raise ValueError(f"attempt.{key} exceeds total budget")
    runtime = value["runtime"]
    for key in ("cpus", "timeout_seconds"):
        number = runtime[key]
        if type(number) not in (int, float) or not math.isfinite(number) or number <= 0:
            raise ValueError(f"runtime.{key} must be positive and finite")
    for key in ("memory_mb", "pids", "tmpfs_mb", "max_output_bytes"):
        if type(runtime[key]) is not int or runtime[key] <= 0:
            raise ValueError(f"runtime.{key} must be a positive integer")
    if runtime["engine"] not in ("trusted-local", "docker"):
        raise ValueError("runtime.engine must be trusted-local or docker")
    if not isinstance(runtime["image"], str):
        raise ValueError("runtime.image must be a string")
    if runtime["engine"] == "docker":
        DockerRuntime(runtime["image"])
    elif runtime["image"]:
        raise ValueError("trusted-local image must be empty")
    task = value["task"]
    if task["id"] != "integer-sum":
        raise ValueError("only integer-sum is implemented")
    if type(task["minimum_improvement"]) not in (int, float) or not math.isfinite(task["minimum_improvement"]) or task["minimum_improvement"] < 0:
        raise ValueError("minimum_improvement must be nonnegative and finite")
    for key in ("development_cases", "selection_cases"):
        cases = task[key]
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"task.{key} must contain cases")
        for case in cases:
            if not isinstance(case, list) or len(case) > 16 or any(type(n) is not int or abs(n) > 10**30 for n in case):
                raise ValueError(f"invalid integer-sum case in {key}")
    lineages = value["lineages"]
    if not isinstance(lineages, list) or not lineages:
        raise ValueError("lineages must be a nonempty array")
    seen = set()
    for lineage in lineages:
        if not isinstance(lineage, dict):
            raise ValueError("lineage must be a table")
        _exact_keys(lineage, required={"id", "origin", "model"}, scope="lineage")
        identifier = lineage["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", identifier) or identifier in seen:
            raise ValueError("lineage IDs must be safe and unique")
        seen.add(identifier)
        if lineage["origin"] not in ("loop", "recursive", "reduce"):
            raise ValueError("unknown seed origin")
        if lineage["model"] != "scripted-v1":
            raise ValueError("only scripted-v1 is implemented; API adapters are not connected")
    return value


def load_config(path: Path) -> dict:
    return validate_config(tomllib.loads(Path(path).read_text(encoding="utf-8")))
