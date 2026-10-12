import json
import tempfile
import unittest
from pathlib import Path

from iah_arena.package_attempts import PackageAttempts
from iah_arena.runtime import RuntimeLimits, RuntimeResult


class EditingRuntime:
    def __init__(self, crash=False):
        self.commands = []
        self.crash = crash

    def run(self, workspace, request, limits):
        self.commands.append(request.argv)
        (workspace / "agent.json").write_text('{"schema_version":1,"argv":["python3","next.py"]}')
        (workspace / "next.py").write_text("print('next')")
        if self.crash:
            raise KeyboardInterrupt()
        return RuntimeResult(0, False, 1, "done")


class PackageAttemptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        seed = self.root / "seed"
        seed.mkdir()
        (seed / "agent.json").write_text('{"schema_version":1,"argv":["python3","first.py"]}')
        (seed / "first.py").write_text("pass")
        self.controller = PackageAttempts(self.root / "state", "one")
        self.original = self.controller.initialize(seed)

    def tearDown(self):
        self.tmp.cleanup()

    def run_attempt(self, number, decision=True, runtime=None, evaluator=None):
        return self.controller.run(epoch=1, attempt=number, runtime=runtime or EditingRuntime(),
                                   limits=RuntimeLimits(1, 128, 32, 5), task_text="Task",
                                   evaluator=evaluator or (lambda _: {"accepted": decision, "reason": "test decision"}))

    def test_promoted_entry_is_used_next_time_and_original_survives(self):
        runtime = EditingRuntime()
        first = self.run_attempt(1, runtime=runtime)
        self.assertEqual(first["generation"], 1)
        self.assertFalse((self.original / "next.py").exists())
        self.run_attempt(2, runtime=runtime)
        self.assertEqual(runtime.commands[0][1], "first.py")
        self.assertEqual(runtime.commands[1][1], "next.py")
        self.assertTrue((Path(first["path"]) / "decision.json").exists())

    def test_rejection_preserves_candidate_but_not_as_current(self):
        result = self.run_attempt(1, decision=False)
        self.assertEqual(result["generation"], 0)
        self.assertTrue((Path(result["path"]) / "files" / "next.py").exists())
        self.assertEqual(self.controller.manager.current_files(), self.original)

    def test_mutating_evaluator_is_rejected(self):
        def mutate(path):
            (path / "extra").write_text("x")
            return {"accepted": True, "reason": "bad evaluator"}
        with self.assertRaisesRegex(ValueError, "mutated"):
            self.run_attempt(1, evaluator=mutate)
        self.assertEqual(self.controller.manager.current_generation(), 0)

    def test_interrupt_never_promotes_and_attempt_id_cannot_replay(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_attempt(1, runtime=EditingRuntime(crash=True))
        self.assertEqual(self.controller.manager.current_generation(), 0)
        with self.assertRaises(FileExistsError):
            self.run_attempt(1)
        self.assertEqual(self.run_attempt(2)["generation"], 1)

    def test_external_change_to_accepted_package_blocks_run(self):
        (self.original / "first.py").write_text("changed")
        with self.assertRaisesRegex(ValueError, "outside controller"):
            self.run_attempt(1)

    def test_rate_limit_cannot_be_bypassed_by_omitting_setting(self):
        from iah_arena.iteration_rate import IterationRate, IterationRateLimited
        args = dict(epoch=1, runtime=EditingRuntime(), limits=RuntimeLimits(1, 128, 32, 5),
                    task_text="Task", evaluator=lambda _: {"accepted": False, "reason": "test"})
        self.controller.run(attempt=1, rate=IterationRate(1, 3600), **args)
        with self.assertRaises(IterationRateLimited):
            self.controller.run(attempt=2, rate=IterationRate(1, 3600), **args)
        with self.assertRaises(ValueError):
            self.controller.run(attempt=2, **args)
