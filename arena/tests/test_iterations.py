import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iah_arena import __version__
from iah_arena.iteration_config import load_config, validate_config
from iah_arena.iterations import create_iterations, continue_iterations, read_state
from iah_arena.locking import FileLock, LockUnavailable
from iah_arena.providers import ToolCall
from iah_arena.runtime import RuntimeResult
from iah_arena.tools import EditBudget, WorkspaceToolExecutor

EXAMPLE = Path(__file__).resolve().parents[1] / "iteration.example.toml"


class FixtureRuntime:
    def run(self, workspace, request, limits):
        values = json.loads(request.argv[-1])
        source = (workspace / "solver.py").read_text(encoding="utf-8")
        result = sum(v for v in values if v >= 0) if "if v >= 0" in source else sum(values)
        return RuntimeResult(0, False, 1, str(result))


class IterationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.config = self.root / "settings.toml"
        self.config.write_bytes(EXAMPLE.read_bytes())
        self.run = self.root / "run"
        self.runtime_patch = patch("iah_arena.iterations._runtime", return_value=FixtureRuntime())
        self.runtime_patch.start()

    def tearDown(self):
        self.runtime_patch.stop()
        self.temporary.cleanup()

    def create(self):
        return create_iterations(self.config, self.run)

    def resume(self, steps=None):
        return continue_iterations(self.run, steps=steps, progress=lambda _: None)

    def test_pause_resume_rotation_and_plateau(self):
        self.create()
        paused = self.resume(steps=2)
        self.assertEqual(paused["status"], "paused")
        self.assertEqual([h["lineage"] for h in paused["history"]], ["lineage-a", "lineage-b"])
        # Editing the original settings does not change the saved run.
        self.config.write_text("broken original file", encoding="utf-8")
        final = self.resume()
        self.assertEqual(final["status"], "complete")
        self.assertEqual([h["lineage"] for h in final["history"]],
                         ["lineage-a", "lineage-b", "lineage-c", "lineage-b", "lineage-c", "lineage-a", "lineage-c", "lineage-a", "lineage-b"])
        for row in final["lineages"].values():
            self.assertEqual(row["generation"], 1)
            self.assertEqual(row["attempts"], 3)
            self.assertEqual(row["stop_reason"], "plateau")
            self.assertEqual(row["usage"]["model_calls"], 12)
            self.assertEqual(row["usage"]["edit_operations"], 3)
            self.assertEqual(row["usage"]["compute_seconds"], 45)
        self.assertEqual(self.resume(), final)

    def test_snapshot_edit_is_rejected(self):
        self.create()
        frozen = self.run / "config.toml"
        frozen.write_text(frozen.read_text() + "\n# edit\n")
        with self.assertRaisesRegex(ValueError, "frozen configuration changed"):
            self.resume()

    def test_source_change_is_rejected(self):
        self.create()
        with patch("iah_arena.iterations._source_digest", return_value="changed"):
            with self.assertRaisesRegex(ValueError, "source changed"):
                self.resume()

    def test_pause_request_finishes_current_attempt_then_resumes(self):
        from iah_arena.iterations import request_pause
        self.create()
        def progress(message):
            if "epoch=" in message:
                request_pause(self.run)
        state = continue_iterations(self.run, progress=progress)
        self.assertEqual(state["status"], "paused")
        self.assertEqual(len(state["history"]), 1)
        self.assertEqual(state["lineages"]["lineage-a"]["generation"], 1)
        self.assertEqual(self.resume(steps=1)["cursor"], 2)

    def test_state_corruption_is_rejected(self):
        self.create()
        path = self.run / "iteration-state.json"
        value = json.loads(path.read_text())
        value["payload"] += " "
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.resume()

    def test_budget_exhaustion_stops_before_next_attempt(self):
        self.config.write_text(EXAMPLE.read_text().replace("model_calls = 40", "model_calls = 4"))
        self.create()
        final = self.resume()
        for row in final["lineages"].values():
            self.assertEqual(row["attempts"], 1)
            self.assertEqual(row["usage"]["model_calls"], 4)
            self.assertEqual(row["stop_reason"], "budget_exhausted")

    def test_interruption_keeps_reservation_and_does_not_replay(self):
        self.create()
        with patch("iah_arena.iterations._perform", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.resume()
        interrupted = read_state(self.run)
        self.assertIsNotNone(interrupted["inflight"])
        self.assertEqual(interrupted["lineages"]["lineage-a"]["usage"]["compute_seconds"], 90)
        resumed = self.resume(steps=1)
        self.assertEqual(resumed["history"][0]["status"], "interrupted")
        self.assertEqual(resumed["history"][1]["lineage"], "lineage-b")
        self.assertEqual(resumed["lineages"]["lineage-a"]["generation"], 0)
        self.assertEqual(resumed["lineages"]["lineage-a"]["usage"]["compute_seconds"], 90)

    def test_completed_but_uncheckpointed_attempt_is_not_promoted_on_resume(self):
        from iah_arena.iterations import _perform
        self.create()
        def crash_after_attempt(*args, **kwargs):
            result = _perform(*args, **kwargs)
            self.assertTrue(result["accepted"])
            raise KeyboardInterrupt
        with patch("iah_arena.iterations._perform", side_effect=crash_after_attempt):
            with self.assertRaises(KeyboardInterrupt):
                self.resume()
        resumed = self.resume(steps=1)
        row = resumed["lineages"]["lineage-a"]
        self.assertEqual(row["generation"], 0)
        self.assertEqual(row["accepted_path"], "seeds/lineage-a")
        self.assertTrue((self.run / "attempt-000001/artifacts").exists())

    def test_compute_budget_and_failure_stopping(self):
        self.config.write_text(EXAMPLE.read_text().replace("compute_seconds = 90", "compute_seconds = 1"))
        self.create()
        final = self.resume()
        for row in final["lineages"].values():
            self.assertEqual(row["stop_reason"], "failure_limit")
            self.assertEqual(row["usage"]["compute_seconds"], 2)
            self.assertEqual(row["usage"]["model_calls"], 0)
            self.assertEqual(row["generation"], 0)

    def test_concurrent_runner_is_rejected(self):
        self.create()
        with FileLock(self.run / ".iteration.lock"):
            with self.assertRaises(LockUnavailable):
                self.resume()

    def test_existing_directory_and_invalid_config_are_not_overwritten(self):
        self.create()
        with self.assertRaises(FileExistsError):
            self.create()
        base = load_config(EXAMPLE)
        bad_configs = []
        for section, key, value in (("run", "max_epochs", True), ("runtime", "cpus", float("nan")),
                                    ("total", "model_calls", -1), ("task", "selection_cases", [])):
            bad = copy.deepcopy(base)
            bad[section][key] = value
            bad_configs.append(bad)
        bad = copy.deepcopy(base)
        bad["api_key"] = "must-not-be-accepted"
        bad_configs.append(bad)
        bad = copy.deepcopy(base)
        bad["lineages"][1]["id"] = bad["lineages"][0]["id"]
        bad_configs.append(bad)
        bad = copy.deepcopy(base)
        bad["lineages"][0]["model"] = "unimplemented-provider"
        bad_configs.append(bad)
        for bad in bad_configs:
            with self.subTest(config=bad), self.assertRaises(ValueError):
                validate_config(bad)

    def test_package_version_matches_metadata(self):
        import tomllib
        data = tomllib.loads((EXAMPLE.parent / "pyproject.toml").read_text())
        self.assertEqual(data["project"]["version"], __version__)


class EditBudgetTests(unittest.TestCase):
    def test_repeated_writes_consume_budget_and_refusal_preserves_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            budget = EditBudget(6, 2)
            executor = WorkspaceToolExecutor(root, public_test_runner=lambda _: {"passed": True}, edit_budget=budget)
            first = executor.execute(ToolCall("1", "write_file", {"path": "a", "content": "abc", "expected_sha256": None}))
            self.assertFalse(first.is_error)
            second = executor.execute(ToolCall("2", "write_file", {"path": "a", "content": "xyz", "expected_sha256": first.output["sha256"]}))
            self.assertFalse(second.is_error)
            third = executor.execute(ToolCall("3", "delete_file", {"path": "a", "expected_sha256": second.output["sha256"]}))
            self.assertTrue(third.is_error)
            self.assertEqual((root / "a").read_bytes(), b"xyz")
            self.assertEqual((budget.bytes_used, budget.operations_used), (6, 2))

    def test_failed_write_does_not_charge(self):
        with tempfile.TemporaryDirectory() as temporary:
            budget = EditBudget(100, 1)
            executor = WorkspaceToolExecutor(Path(temporary), public_test_runner=lambda _: {}, edit_budget=budget)
            with patch("iah_arena.tools.os.replace", side_effect=OSError("disk error")):
                result = executor.execute(ToolCall("1", "write_file", {"path": "a", "content": "abc", "expected_sha256": None}))
            self.assertTrue(result.is_error)
            self.assertEqual((budget.bytes_used, budget.operations_used), (0, 0))


if __name__ == "__main__":
    unittest.main()
