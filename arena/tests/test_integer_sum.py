import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from iah_arena.demo import TrustedDemoRuntime, run_task_demo
from iah_arena.fitness import FitnessPolicy, MetricDirection, MetricSpec
from iah_arena.runtime import RuntimeResult
from iah_arena.tasks.integer_sum import IntegerSumTask, SEEDS, SOLUTIONS
from iah_arena.docker_runtime import DockerRuntimeError
from iah_arena.__main__ import main


class ReplyRuntime:
    def __init__(self, reply):
        self.reply = reply
        self.requests = []

    def run(self, workspace, request, limits):
        self.requests.append(request)
        return self.reply(request)


class IntegerSumTests(unittest.TestCase):
    def test_cli_preflight_failure_creates_no_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "must-not-exist"
            argv = ["iah_arena", "task-demo", "--image", "sha256:" + "a" * 64, "--output-dir", str(output)]
            with patch("sys.argv", argv), patch(
                "iah_arena.__main__.DockerRuntime.check_ready",
                side_effect=DockerRuntimeError("engine unavailable"),
            ), redirect_stdout(StringIO()) as console:
                self.assertEqual(main(), 1)
            self.assertIn("engine unavailable", console.getvalue())
            self.assertFalse(output.exists())

    def test_exact_oracle_and_candidate_boundary(self):
        runtime = ReplyRuntime(lambda r: RuntimeResult(0, False, 1, str(sum(json.loads(r.argv[-1])))))
        task = IntegerSumTask(runtime)
        result = task.make_evaluator(task.curriculum.stages[0])(Path("unused"))
        self.assertEqual(result["fitness"]["correct_fraction"], 1.0)
        self.assertNotIn("accepted", result)
        self.assertTrue(all(r.workspace_read_only and not r.extra_mounts for r in runtime.requests))

    def test_invalid_wrong_and_failed_outputs_cannot_score_as_correct(self):
        replies = (
            RuntimeResult(0, False, 1, "true"),
            RuntimeResult(0, False, 1, "0.0"),
            RuntimeResult(0, False, 1, "[]"),
            RuntimeResult(0, False, 1, "0\n0"),
            RuntimeResult(1, False, 1, "0"),
            RuntimeResult(None, True, 1, "0"),
            RuntimeResult(0, False, 1, "0", output_truncated=True),
        )
        for reply in replies:
            with self.subTest(reply=reply):
                task = IntegerSumTask(ReplyRuntime(lambda r: reply))
                result = task.make_evaluator(task.curriculum.stages[0])(Path("unused"))
                self.assertEqual(result["fitness"]["correct_fraction"], 0.0)
                self.assertEqual(result["timed_out_cases"], result["cases"] if reply.timed_out else 0)
                self.assertEqual(result["execution_failures"], result["cases"] if not reply.succeeded else 0)
                self.assertEqual(result["truncated_cases"], result["cases"] if reply.output_truncated else 0)
        task = IntegerSumTask(ReplyRuntime(lambda r: RuntimeResult(0, False, 1, "999")))
        self.assertEqual(task.make_evaluator(task.curriculum.stages[0])(Path("unused"))["fitness"]["correct_fraction"], 0.0)

    def test_trusted_runtime_rejects_modified_source_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "solver.py").write_text("raise RuntimeError('must not execute')", encoding="utf-8")
            task = IntegerSumTask(TrustedDemoRuntime(frozenset(SOLUTIONS.values())))
            with self.assertRaisesRegex(ValueError, "unrecognized source"):
                task.make_evaluator(task.curriculum.stages[0])(workspace)

    def test_three_lineages_run_and_keep_separate_programs_and_artifacts(self):
        runtime = TrustedDemoRuntime(frozenset((*SEEDS.values(), *SOLUTIONS.values())))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "demo"
            variants = {name: (seed, SOLUTIONS[name]) for name, seed in SEEDS.items()}
            task = IntegerSumTask(runtime)
            policy = FitnessPolicy((MetricSpec("correct_fraction", MetricDirection.MAXIMIZE),))
            summary = run_task_demo(task, variants, output, environment="test", policy=policy, progress=lambda _: None)
            self.assertTrue(summary["success"])
            self.assertEqual(len(summary["lineages"]), 3)
            self.assertEqual(len({row["artifact_id"] for row in summary["lineages"]}), 3)
            for row in summary["lineages"]:
                self.assertEqual(row["baseline_evaluation"]["execution_failures"], 0)
                self.assertEqual(row["candidate_evaluation"]["timed_out_cases"], 0)
                self.assertLess(row["before"]["correct_fraction"], row["after"]["correct_fraction"])
                self.assertEqual(row["after"]["correct_fraction"], 1.0)
                workspace = output / "state" / "lineages" / row["lineage"] / "workspace"
                self.assertEqual((workspace / "accepted/gen-0000/files/solver.py").read_bytes(), SEEDS[row["origin"]].encode())
                self.assertEqual((workspace / "accepted/gen-0001/files/solver.py").read_bytes(), SOLUTIONS[row["origin"]].encode())
                events = (workspace.parent / "events.jsonl").read_text(encoding="utf-8")
                for other in summary["lineages"]:
                    if other["lineage"] != row["lineage"]:
                        self.assertNotIn(other["lineage"], events)
            for name in ("report.html", "summary.json", "manifest.json", "telemetry/metrics.csv"):
                self.assertTrue((output / name).is_file())
            with self.assertRaises(FileExistsError):
                run_task_demo(task, variants, output, environment="test", policy=policy, progress=lambda _: None)

    def test_lineage_failure_is_reported_and_does_not_stop_others(self):
        task = IntegerSumTask(TrustedDemoRuntime(frozenset((*SEEDS.values(), *SOLUTIONS.values()))))
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_task_demo(
                task, {"broken": ("unknown source", "unknown source"), "loop": (SEEDS["loop"], SOLUTIONS["loop"])},
                Path(temporary) / "demo", environment="test", progress=lambda _: None,
                policy=FitnessPolicy((MetricSpec("correct_fraction", MetricDirection.MAXIMIZE),)),
            )
            self.assertFalse(summary["success"])
            self.assertEqual(len(summary["failures"]), 1)
            self.assertTrue(summary["lineages"][0]["accepted"])

    def test_equivalent_solution_is_not_promoted(self):
        task = IntegerSumTask(TrustedDemoRuntime(frozenset(SOLUTIONS.values())))
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_task_demo(
                task, {"loop": (SOLUTIONS["loop"], SOLUTIONS["reduce"])},
                Path(temporary) / "demo", environment="test", progress=lambda _: None,
                policy=FitnessPolicy((MetricSpec("correct_fraction", MetricDirection.MAXIMIZE),)),
            )
            self.assertFalse(summary["success"])
            self.assertFalse(summary["lineages"][0]["accepted"])
            self.assertEqual(summary["lineages"][0]["generation"], 0)


if __name__ == "__main__":
    unittest.main()
