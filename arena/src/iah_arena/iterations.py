"""Durable exploratory loop with bounded attempts and conservative crash recovery."""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import asdict, replace
from pathlib import Path

from . import __version__
from .artifacts import ArtifactProvenance
from .budgets import BudgetLedger, BudgetLimits
from .controller import ArenaController
from .demo import TrustedDemoRuntime
from .docker_runtime import DockerRuntime
from .fitness import AcceptanceMode, FitnessPolicy, FitnessVector, MetricDirection, MetricSpec, PolicyEvaluator
from .iteration_config import BUDGET_FIELDS, load_config
from .locking import FileLock
from .providers import DecisionContext, ProviderTurn, ScriptedProvider, ToolCall
from .openai_provider import OpenAIProvider, OpenAITransport
from .prompts import ImprovementPromptBuilder, InformationBudget
from .runtime import RuntimeLimits
from .sessions import SessionLimits
from .tasks.integer_sum import IntegerSumTask, SEEDS, SOLUTIONS
from .tools import CANONICAL_TOOLS, EditBudget


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_digest() -> str:
    root = Path(__file__).parent
    return _digest(json.dumps({p.relative_to(root).as_posix(): _digest(p.read_bytes())
                              for p in sorted(root.rglob("*.py"))}, sort_keys=True).encode())


def _save(path: Path, value: dict) -> None:
    body = json.dumps(value, sort_keys=True, allow_nan=False)
    envelope = json.dumps({"sha256": _digest(body.encode()), "payload": body}, indent=2)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(envelope)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def read_state(directory: Path) -> dict:
    envelope = json.loads((Path(directory) / "iteration-state.json").read_text(encoding="utf-8"))
    if _digest(envelope["payload"].encode()) != envelope["sha256"]:
        raise ValueError("iteration state checksum mismatch")
    return json.loads(envelope["payload"])


def request_pause(directory: Path) -> None:
    directory = Path(directory)
    read_state(directory)
    (directory / "pause.request").touch()


class MeteredRuntime:
    def __init__(self, runtime, allowance: int):
        self.runtime = runtime
        self.allowance = allowance
        self.used = 0

    def run(self, workspace, request, limits):
        remaining = self.allowance - self.used
        if remaining <= 0:
            raise RuntimeError("compute budget exhausted")
        timeout = min(limits.timeout_seconds, remaining)
        started = time.monotonic()
        try:
            return self.runtime.run(workspace, request, replace(limits, timeout_seconds=timeout))
        finally:
            # Conservative whole seconds including Docker startup and cleanup.
            self.used += min(remaining, max(1, math.ceil(time.monotonic() - started)))


def _runtime(config):
    settings = config["runtime"]
    if settings["engine"] == "docker":
        runtime = DockerRuntime(settings["image"])
        runtime.check_ready()
        return runtime
    return TrustedDemoRuntime(frozenset((*SEEDS.values(), *SOLUTIONS.values())))


def _provider_prerequisites(config):
    if any(item["model"].startswith("openai/") for item in config["lineages"]):
        settings = config["openai"]
        OpenAITransport(settings["key_env"], settings["timeout_seconds"])


def create_iterations(config_path: Path, directory: Path) -> dict:
    config_path, directory = Path(config_path), Path(directory)
    raw = config_path.read_bytes()
    config = load_config(config_path)
    _provider_prerequisites(config)
    _runtime(config)  # Prerequisites before creating any run files.
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "config.toml").write_bytes(raw)
    state = {
        "version": __version__, "source_digest": _source_digest(),
        "config_sha256": _digest(raw), "cursor": 0, "status": "paused",
        "inflight": None, "history": [], "lineages": {},
    }
    for item in config["lineages"]:
        seed = directory / "seeds" / item["id"]
        seed.mkdir(parents=True)
        (seed / "solver.py").write_bytes(SEEDS[item["origin"]].encode())
        state["lineages"][item["id"]] = {
            "accepted_path": seed.relative_to(directory).as_posix(),
            "accepted_sha256": _digest((seed / "solver.py").read_bytes()),
            "generation": 0, "attempts": 0, "stale": 0, "failures": 0,
            "stop_reason": None, "usage": dict.fromkeys(sorted(BUDGET_FIELDS), 0),
        }
    _save(directory / "iteration-state.json", state)
    return state


def _perform(config, directory, state, item, job, runtime, ledgers):
    lineage = item["id"]
    row = state["lineages"][lineage]
    current = (directory / row["accepted_path"]).resolve()
    if not current.is_relative_to(directory.resolve()):
        raise ValueError("accepted workspace escapes run directory")
    if _digest((current / "solver.py").read_bytes()) != row["accepted_sha256"]:
        raise ValueError("accepted program changed outside Arena")
    job.mkdir()
    controller = ArenaController(job / "state", artifact_dir=job / "artifacts")
    controller.initialize_lineage(lineage, origin=item["origin"])
    controller.initialize_workspace(lineage, current)
    settings = config["runtime"]
    limits = RuntimeLimits(**{k: v for k, v in settings.items() if k not in {"engine", "image"}})
    metered, api, edits = ledgers
    task = IntegerSumTask(metered, limits=limits,
                          development=config["task"]["development_cases"],
                          selection=config["task"]["selection_cases"])
    stage = task.curriculum.stages[0]
    evaluator = task.make_evaluator(stage)
    baseline = evaluator(current)
    policy = FitnessPolicy(
        (MetricSpec("correct_fraction", MetricDirection.MAXIMIZE, weight=1),),
        mode=AcceptanceMode.WEIGHTED,
        minimum_scalar_improvement=config["task"]["minimum_improvement"],
    )
    source = (current / "solver.py").read_bytes()
    provider = ScriptedProvider((
        ProviderTurn(tool_calls=(ToolCall("read", "read_file", {"path": "solver.py"}),)),
        ProviderTurn(tool_calls=(ToolCall("write", "write_file", {
            "path": "solver.py", "content": SOLUTIONS[item["origin"]], "expected_sha256": _digest(source),
        }),)),
        ProviderTurn(tool_calls=(ToolCall("tests", "run_public_tests", {}),)),
        ProviderTurn(tool_calls=(ToolCall("submit", "submit_candidate", {"claim": {
            "bottleneck": "scripted signed-sum fixture", "hypothesis": "include negative values",
            "changes": ["apply bundled program"], "expected_effect": "correct sums",
            "risks": ["scripted demonstration, no autonomous discovery"],
        }}),)),
    ))
    if item["model"].startswith("openai/"):
        provider = OpenAIProvider(item["model"].removeprefix("openai/"), config["openai"], api)
    context = DecisionContext(lineage, 1, 0, 1, task.objective(stage), baseline["fitness"],
                              asdict(api.remaining()), {"files": ["solver.py"], "total_bytes": len(source)})
    history = [h for h in state["history"] if h["lineage"] == lineage]
    count = config["information"]["max_history_items"]
    recent = [{"attempt": h["attempt"], "status": h["status"]} for h in history[-count:]] if count else []
    context = ImprovementPromptBuilder(InformationBudget(**config["information"])).attach(
        context, CANONICAL_TOOLS, recent_history=recent,
    )
    result = controller.run_attempt(
        lineage_id=lineage, epoch=1, attempt=1, provider=provider, context=context,
        budget=api, edit_budget=edits,
        **config["workspace"],
        limits=SessionLimits(config["attempt"]["model_calls"], config["run"]["max_tool_calls"]),
        public_test_runner=task.make_public_test_runner(stage),
        evaluator=PolicyEvaluator(evaluator=evaluator, policy=policy, incumbent=FitnessVector(baseline["fitness"])),
        artifact_provenance=ArtifactProvenance(
            lineage, 1, 1, 1, 0, task.task_id, task.task_version, task.evaluator_version,
            task.curriculum.digest, settings["image"] or "trusted-local", state["source_digest"], 0,
            item["model"], metadata={"config_sha256": state["config_sha256"], "iteration": row["attempts"]},
        ),
    )
    controller.verify_lineage(lineage)
    candidate = (result.files_path / "solver.py").read_bytes()
    return {
        "accepted": result.accepted, "baseline": baseline, "evaluation": dict(result.evaluation),
        "accepted_path": result.files_path.relative_to(directory).as_posix() if result.accepted else row["accepted_path"],
        "accepted_sha256": _digest(candidate) if result.accepted else row["accepted_sha256"],
        "net_changed_files": int(source != candidate),
        "net_replaced_bytes": len(source) + len(candidate) if source != candidate else 0,
        "artifact_id": result.artifact_id,
    }


def continue_iterations(directory: Path, *, steps: int | None = None, progress=print) -> dict:
    directory = Path(directory).resolve()
    if steps is not None and (type(steps) is not int or steps <= 0):
        raise ValueError("steps must be positive")
    if not (directory / "iteration-state.json").is_file():
        raise ValueError("no initialized iterative run at this path")
    with FileLock(directory / ".iteration.lock"):
        state = read_state(directory)
        raw = (directory / "config.toml").read_bytes()
        if _digest(raw) != state["config_sha256"]:
            raise ValueError("frozen configuration changed; create a new run")
        if state["version"] != __version__ or state["source_digest"] != _source_digest():
            raise ValueError("Arena source changed; resume with the original version/source")
        config = load_config(directory / "config.toml")
        if state["status"] == "complete":
            return state
        _provider_prerequisites(config)
        if state["inflight"] is not None:
            lost = state["inflight"]
            row = state["lineages"][lost["lineage"]]
            row["failures"] += 1
            row["stale"] += 1
            state["history"].append({**lost, "status": "interrupted", "budget": "full reservation retained"})
            state["inflight"] = None
            _save(directory / "iteration-state.json", state)
        runtime = _runtime(config)
        # Explicit resume clears a prior pause request; new requests are checked
        # between attempts and do not interrupt an in-flight candidate evaluation.
        (directory / "pause.request").unlink(missing_ok=True)
        items = config["lineages"]
        schedule = []
        for epoch in range(config["run"]["max_epochs"]):
            offset = epoch % len(items)
            schedule.extend((epoch + 1, item) for item in items[offset:] + items[:offset])
        completed = 0
        while state["cursor"] < len(schedule):
            if (directory / "pause.request").exists():
                break
            if steps is not None and completed >= steps:
                break
            epoch, item = schedule[state["cursor"]]
            row = state["lineages"][item["id"]]
            rules = config["run"]
            if row["stop_reason"] is None:
                if row["failures"] >= rules["failure_limit"]:
                    row["stop_reason"] = "failure_limit"
                elif row["attempts"] >= rules["min_attempts"] and row["stale"] >= rules["plateau_patience"]:
                    row["stop_reason"] = "plateau"
                elif any(row["usage"][k] + config["attempt"][k] > config["total"][k] for k in BUDGET_FIELDS):
                    row["stop_reason"] = "budget_exhausted"
            slot = state["cursor"]
            state["cursor"] += 1
            if row["stop_reason"]:
                _save(directory / "iteration-state.json", state)
                continue
            row["attempts"] += 1
            for key in BUDGET_FIELDS:
                row["usage"][key] += config["attempt"][key]
            job = directory / f"attempt-{slot + 1:06d}"
            state["inflight"] = {"lineage": item["id"], "epoch": epoch, "attempt": row["attempts"], "job": job.name}
            state["status"] = "running"
            _save(directory / "iteration-state.json", state)
            cap = config["attempt"]
            api = BudgetLedger(BudgetLimits(cap["model_calls"], cap["input_tokens"], cap["output_tokens"], cap["cost_microusd"], 0))
            edits = EditBudget(cap["edit_bytes"], cap["edit_operations"])
            metered = MeteredRuntime(runtime, cap["compute_seconds"])
            progress(f"{item['id']}: epoch={epoch} attempt={row['attempts']}")
            try:
                result = _perform(config, directory, state, item, job, runtime, (metered, api, edits))
                row["failures"] = 0
                row["stale"] = 0 if result["accepted"] else row["stale"] + 1
                if result["accepted"]:
                    row["generation"] += 1
                    row["accepted_path"] = result["accepted_path"]
                    row["accepted_sha256"] = result["accepted_sha256"]
                result["status"] = "accepted" if result["accepted"] else "rejected"
            except Exception as error:
                result = {"status": "failed", "error": f"{type(error).__name__}: {error}"}
                row["failures"] += 1
                row["stale"] += 1
            spent = {k: getattr(api.usage, k) for k in ("model_calls", "input_tokens", "output_tokens", "cost_microusd")}
            spent.update(compute_seconds=metered.used, edit_bytes=edits.bytes_used, edit_operations=edits.operations_used)
            for key in BUDGET_FIELDS:
                row["usage"][key] -= cap[key] - spent[key]
            state["history"].append({**state["inflight"], **result, "spent": spent})
            state["inflight"] = None
            completed += 1
            _save(directory / "iteration-state.json", state)
            progress(f"{item['id']}: {result['status']}; generation={row['generation']}")
        state["status"] = "complete" if state["cursor"] == len(schedule) else "paused"
        if state["status"] == "complete":
            for row in state["lineages"].values():
                row["stop_reason"] = row["stop_reason"] or "max_epochs"
        _save(directory / "iteration-state.json", state)
        (directory / "summary.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state
