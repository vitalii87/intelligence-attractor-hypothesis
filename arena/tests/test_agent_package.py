import json
from pathlib import Path
import tempfile
import unittest

from iah_arena.agent_package import inspect_package, run_package
from iah_arena.runtime import RuntimeLimits, RuntimeResult


class PackageTests(unittest.TestCase):
    def test_entry_reload_and_external_context(self):
        requests = []
        class Runtime:
            def run(self, workspace, request, limits):
                requests.append(request)
                context = json.loads((request.extra_mounts[0].host_path / "context.json").read_text())
                self_test.assertEqual(context["task"], "Solve the supplied task.")
                self_test.assertFalse(context["capabilities"]["model_gateway"])
                self_test.assertTrue(request.extra_mounts[0].read_only)
                self_test.assertFalse(request.workspace_read_only)
                # Simulate package updating its own entry contract and persistent state.
                (workspace / "agent.json").write_text(json.dumps({"schema_version": 1, "argv": ["python3", "next.py"]}))
                (workspace / "memory.txt").write_text("retained")
                return RuntimeResult(0, False, 1, "ok")
        self_test = self
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agent.json").write_text('{"schema_version":1,"argv":["python3","initial.py"]}')
            (root / "initial.py").write_text("pass")
            (root / "next.py").write_text("pass")
            limits = RuntimeLimits(1, 128, 32, 5)
            first = run_package(root, Runtime(), limits, "Solve the supplied task.")
            second = run_package(root, Runtime(), limits, "Solve the supplied task.")
            self.assertTrue(first["changed"])
            self.assertTrue(first["package_valid"])
            self.assertEqual(requests[0].argv[1], "initial.py")
            self.assertEqual(requests[1].argv[1], "next.py")
            self.assertEqual(second["before"]["sha256"], first["after"]["sha256"])
            self.assertFalse((root / "context.json").exists())

    def test_invalid_manifest_and_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for manifest in ({"schema_version": 1, "argv": []}, {"schema_version": True, "argv": ["x"]},
                             {"schema_version": 1, "argv": ["x"], "mounts": []}):
                (root / "agent.json").write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    inspect_package(root)
            (root / "agent.json").write_text('{"schema_version":1,"argv":["x"]}')
            (root / "large").write_bytes(b"x" * 256001)
            with self.assertRaises(ValueError):
                inspect_package(root)

    def test_broken_self_edit_not_valid(self):
        class Runtime:
            def run(self, workspace, request, limits):
                (workspace / "agent.json").write_text("broken")
                return RuntimeResult(1, False, 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agent.json").write_text('{"schema_version":1,"argv":["x"]}')
            result = run_package(root, Runtime(), RuntimeLimits(1, 128, 32, 5), "Task")
            self.assertFalse(result["package_valid"])
            self.assertIsNone(result["after"])
