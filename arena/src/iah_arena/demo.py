"""One scripted integration epoch using the existing task/provider/runtime boundaries."""
from __future__ import annotations

import hashlib
import html
import json
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Mapping

from .artifacts import ArtifactProvenance
from .budgets import BudgetLedger, BudgetLimits
from .controller import ArenaController
from .coordinator import SequentialLineageCoordinator, StepStatus
from .fitness import FitnessPolicy, FitnessVector, PolicyEvaluator
from .prompts import ImprovementPromptBuilder, InformationBudget
from .providers import DecisionContext, ProviderTurn, ScriptedProvider, ToolCall
from .runtime import RuntimeLimits, RuntimeRequest, RuntimeResult, RuntimeRole
from .tasking import TaskPlugin
from .telemetry import TelemetryExporter
from .tools import CANONICAL_TOOLS


class TrustedDemoRuntime:
    """Execute only exact bundled fixtures, never arbitrary candidate code.

    This is not a sandbox. Verified source is passed directly via -c in an empty
    temporary directory, avoiding a second read of a mutable candidate file.
    """

    def __init__(self, allowed_sources: frozenset[str]) -> None:
        self.allowed_sources = frozenset(source.encode("utf-8") for source in allowed_sources)

    def run(self, workspace: Path, request: RuntimeRequest, limits: RuntimeLimits) -> RuntimeResult:
        if (
            request.argv[:4] != ("python3", "-I", "-B", "solver.py")
            or len(request.argv) != 5 or request.extra_mounts
            or request.role is not RuntimeRole.JUDGE or not request.workspace_read_only
        ):
            raise ValueError("trusted demo supports only its fixed solver command")
        source = (workspace / "solver.py").read_bytes()
        if source not in self.allowed_sources:
            raise ValueError("unrecognized source; use Docker for arbitrary candidates")
        values = json.loads(request.argv[4])
        if not isinstance(values, list) or len(values) > 16 or any(
            type(value) is not int or abs(value) > 10**30 for value in values
        ):
            raise ValueError("input is outside trusted demo bounds")
        started = time.monotonic()
        with TemporaryDirectory(prefix="iah-trusted-demo-") as temporary:
            completed = subprocess.run(
                [sys.executable, "-I", "-B", "-c", source.decode("utf-8"), request.argv[4]],
                cwd=temporary, capture_output=True, encoding="utf-8",
                timeout=limits.timeout_seconds, check=False,
            )
        return RuntimeResult(
            completed.returncode, False, round((time.monotonic() - started) * 1000),
            completed.stdout, completed.stderr,
            runtime_metadata={"engine": "trusted-fixtures-only", "sandboxed": False},
        )


def run_task_demo(
    task: TaskPlugin,
    variants: Mapping[str, tuple[str, str]],
    output_dir: Path,
    *,
    environment: str,
    policy: FitnessPolicy,
    progress: Callable[[str], None] = print,
) -> dict:
    """Exercise any compatible task with explicit seed/replacement fixtures.

    Number of lineages comes from variants, never from the Arena core.
    No model calls, hidden suites, convergence analysis, or run-manager holdout
    transitions are performed by this deliberately separate demo command.
    """
    if not variants:
        raise ValueError("at least one demo lineage is required")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    stage = task.curriculum.stages[0]
    controller = ArenaController(output_dir / "state", artifact_dir=output_dir / "artifacts")
    prompt_builder = ImprovementPromptBuilder(InformationBudget(30000, 5, 10, 10, 100000))
    lineages = tuple(f"demo-{index + 1}" for index in range(len(variants)))
    assignments = dict(zip(lineages, variants.items()))
    rows = []
    # Code hashes distinguish an uncommitted working tree as well as Git revisions.
    source_hashes = {
        path.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(Path(__file__).parent.rglob("*.py"))
    }
    source_digest = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
    manifest = {
        "kind": "scripted-integration-demo", "task": task.task_id,
        "task_version": task.task_version, "evaluator_version": task.evaluator_version,
        "curriculum_digest": task.curriculum.digest, "environment": environment,
        "python": sys.version, "arena_source_digest": source_digest,
        "arena_source_hashes": source_hashes,
        "lineages": {key: value[0] for key, value in assignments.items()},
        "selection_cases_public": True, "final_holdout_opened": False,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for lineage, (origin, (seed, _)) in assignments.items():
        controller.initialize_lineage(lineage, origin=origin, metadata={"task": task.task_id, "demo": True})
        with TemporaryDirectory(prefix="iah-demo-seed-") as temporary:
            seed_dir = Path(temporary)
            (seed_dir / "solver.py").write_bytes(seed.encode("utf-8"))
            controller.initialize_workspace(lineage, seed_dir)

    def step(lineage: str, epoch: int) -> dict:
        origin, (_, replacement) = assignments[lineage]
        current = controller.workspace_manager(lineage).current_files()
        raw_evaluator = task.make_evaluator(stage)
        baseline = raw_evaluator(current)
        progress(f"{lineage} ({origin}): baseline={baseline['fitness']}; editing")
        digest = hashlib.sha256((current / "solver.py").read_bytes()).hexdigest()
        provider = ScriptedProvider((
            ProviderTurn(tool_calls=(ToolCall("read", "read_file", {"path": "solver.py"}),)),
            ProviderTurn(tool_calls=(ToolCall("edit", "write_file", {
                "path": "solver.py", "content": replacement, "expected_sha256": digest,
            }),)),
            ProviderTurn(tool_calls=(ToolCall("test", "run_public_tests", {}),)),
            ProviderTurn(tool_calls=(ToolCall("submit", "submit_candidate", {"claim": {
                "bottleneck": "scripted demo seed fails some task inputs",
                "hypothesis": "bundled replacement satisfies the declared interface",
                "changes": ["apply predetermined fixture; no autonomous discovery"],
                "expected_effect": "higher correct_fraction", "risks": ["integration demo only"],
            }}),)),
        ))
        budget = BudgetLedger(BudgetLimits(4, 0, 0, 0, 0))
        context = prompt_builder.attach(DecisionContext(
            lineage, epoch, 0, 1, task.objective(stage), baseline["fitness"],
            asdict(budget.remaining()),
            {"files": ["solver.py"], "total_bytes": (current / "solver.py").stat().st_size},
            stage={"stage_id": stage.stage_id},
        ), CANONICAL_TOOLS)
        result = controller.run_attempt(
            lineage_id=lineage, epoch=epoch, attempt=1, provider=provider,
            context=context, budget=budget,
            public_test_runner=task.make_public_test_runner(stage),
            evaluator=PolicyEvaluator(evaluator=raw_evaluator, policy=policy, incumbent=FitnessVector(baseline["fitness"])),
            artifact_provenance=ArtifactProvenance(
                lineage, epoch, 1, 1, 0, task.task_id, task.task_version,
                task.evaluator_version, task.curriculum.digest, environment,
                f"source-sha256:{source_digest}", 0, "scripted/scripted-v1",
                metadata={"demo": True, "origin": origin},
            ),
        )
        row = {
            "lineage": lineage, "origin": origin, "before": baseline["fitness"],
            "after": result.evaluation.get("fitness"), "accepted": result.accepted,
            "generation": result.generation, "artifact_id": result.artifact_id,
            "provider_turns": result.session.provider_turns,
            "events": controller.verify_lineage(lineage),
            "baseline_evaluation": baseline,
            "candidate_evaluation": dict(result.evaluation),
        }
        rows.append(row)
        progress(f"{lineage}: accepted={result.accepted}; generation={result.generation}; fitness={row['after']}")
        return row

    results = SequentialLineageCoordinator(lineages).run_epoch(1, step)
    failures = [{"lineage": r.lineage_id, "error": r.error_message} for r in results if r.status is StepStatus.FAILED]
    TelemetryExporter(output_dir / "state").export_bundle(lineages, output_dir / "telemetry")
    summary = {
        "kind": "scripted-integration-demo", "task": task.task_id, "lineages": rows,
        "failures": failures, "success": not failures and all(row["accepted"] for row in rows),
        "interpretation": "Infrastructure check only. Predetermined improvements are not evidence for IAH.",
    }
    serialized = json.dumps(summary, indent=2)
    (output_dir / "summary.json").write_text(serialized, encoding="utf-8")
    report = (
        "<!doctype html><html lang='en'><meta charset='utf-8'><title>Arena demo</title>"
        "<body><h1>Arena integration demo</h1><p>Scripted providers; no IAH inference.</p>"
        "<p><a href='summary.json'>Summary</a> | <a href='manifest.json'>Manifest</a> | "
        "<a href='telemetry/metrics.csv'>Metrics CSV</a> | <a href='telemetry/events.csv'>Events CSV</a></p>"
        f"<pre>{html.escape(serialized)}</pre></body></html>"
    )
    (output_dir / "report.html").write_text(report, encoding="utf-8")
    progress(f"Report: {output_dir / 'report.html'}")
    return summary
