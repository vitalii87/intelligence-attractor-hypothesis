"""Small, public integration task, not a confirmatory IAH benchmark."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..runtime import CandidateRuntime, RuntimeLimits, RuntimeRequest, RuntimeRole
from ..tasking import BenchmarkSuite, CurriculumSpec, CurriculumStage, SuiteKind


_HEADER = "import json, sys\nvalues = json.loads(sys.argv[1])\n"
SOLUTIONS = {
    "loop": _HEADER + "total = 0\nfor value in values:\n    total += value\nprint(json.dumps(total))\n",
    "recursive": _HEADER + (
        "def add(items):\n    if not items:\n        return 0\n"
        "    return items[0] + add(items[1:])\nprint(json.dumps(add(values)))\n"
    ),
    "reduce": _HEADER + (
        "from functools import reduce\n"
        "print(json.dumps(reduce(lambda a, b: a + b, values, 0)))\n"
    ),
}
# All seeds expose the same deliberate defect, while keeping different structures.
SEEDS = {
    name: source.replace("values = json.loads(sys.argv[1])", "values = [v for v in json.loads(sys.argv[1]) if v >= 0]")
    for name, source in SOLUTIONS.items()
}
DEVELOPMENT = ((), (1, 2, 3), (-2, 1))
SELECTION = ((0,), (4, 5), (-1,), (3, -7, 2), (-4, -5), (10**20, -10**20, 7))


class IntegerSumTask:
    task_id = "integer-sum"
    task_version = "demo-v1"
    evaluator_version = "exact-integer-v1"
    curriculum = CurriculumSpec(
        "integer-sum-demo", "1",
        (CurriculumStage("small", 0, {"max_items": 16}, None, confirmatory=False),),
        tuple(BenchmarkSuite(
            f"integer-sum-{kind.value}", kind, "demo-v1",
            "public integration fixtures" if kind in {SuiteKind.DEVELOPMENT, SuiteKind.SELECTION}
            else "reserved identity; not implemented or opened by this demo",
        ) for kind in SuiteKind),
    )

    def __init__(self, runtime: CandidateRuntime) -> None:
        self.runtime = runtime
        self.limits = RuntimeLimits(1, 128, 32, 5, tmpfs_mb=16, max_output_bytes=4096)

    def objective(self, stage: CurriculumStage) -> Mapping[str, Any]:
        self._validate_stage(stage)
        return {
            "task": self.task_id,
            "instruction": "Return the exact sum of a JSON list of signed integers, including the empty list.",
            "interface": "python3 -I -B solver.py '<JSON list>'; stdout must be one JSON integer",
            "design_space": "Python 3 standard library; solver.py entry point; any internal structure",
            "metric": "correct_fraction; maximize; strictly improve over incumbent",
            "scope": "public, scripted integration demo; no convergence inference",
        }

    def make_public_test_runner(self, stage: CurriculumStage):
        self._validate_stage(stage)

        def run(workspace: Path) -> Mapping[str, Any]:
            result = self._evaluate(workspace, DEVELOPMENT)
            return {"passed": result["fitness"]["correct_fraction"] == 1.0, **result}

        return run

    def make_evaluator(self, stage: CurriculumStage):
        self._validate_stage(stage)
        return lambda workspace: self._evaluate(workspace, SELECTION)

    def _validate_stage(self, stage: CurriculumStage) -> None:
        if stage != self.curriculum.stages[0]:
            raise ValueError("unsupported integer-sum stage")

    def _evaluate(self, workspace: Path, cases: tuple[tuple[int, ...], ...]) -> Mapping[str, Any]:
        correct = 0
        failures = 0
        duration_ms = 0
        timed_out_cases = 0
        execution_failures = 0
        truncated_cases = 0
        for values in cases:
            request = RuntimeRequest(
                ("python3", "-I", "-B", "solver.py", json.dumps(values)),
                RuntimeRole.JUDGE, workspace_read_only=True,
            )
            result = self.runtime.run(workspace, request, self.limits)
            duration_ms += result.duration_ms
            timed_out_cases += int(result.timed_out)
            execution_failures += int(not result.succeeded)
            truncated_cases += int(result.output_truncated)
            if not result.succeeded or result.output_truncated:
                failures += 1
                continue
            try:
                answer = json.loads(result.stdout)
            except (ValueError, RecursionError):
                failures += 1
                continue
            if type(answer) is not int:
                failures += 1
                continue
            correct += answer == sum(values)
        return {
            "fitness": {"correct_fraction": correct / len(cases)},
            "correct": correct, "cases": len(cases), "invalid_outputs": failures,
            "duration_ms": duration_ms,
            "timed_out_cases": timed_out_cases,
            "execution_failures": execution_failures,
            "truncated_cases": truncated_cases,
        }
