import hashlib
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iah_arena.providers import ToolCall
from iah_arena.tools import WorkspaceToolExecutor


class WorkspaceToolExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        (self.workspace / "solver.txt").write_text("old\n", encoding="utf-8")
        self.executor = WorkspaceToolExecutor(
            self.workspace,
            public_test_runner=lambda workspace: {
                "passed": (workspace / "solver.txt").read_text(encoding="utf-8") == "new\n"
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def call(self, name: str, arguments: dict[str, object]):
        # Existing editing tests act on a freshly observed file by default.
        # Conflict tests supply the earlier digest explicitly.
        arguments = dict(arguments)
        if name in {"write_file", "replace_text", "delete_file"} and "expected_sha256" not in arguments:
            path = self.workspace / arguments["path"]
            arguments["expected_sha256"] = (
                hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            )
        return self.executor.execute(ToolCall("call", name, arguments))

    @staticmethod
    def claim() -> dict[str, object]:
        return {
            "claim": {
                "bottleneck": "old marker",
                "hypothesis": "new marker passes",
                "changes": ["replace marker"],
                "expected_effect": "tests pass",
                "risks": [],
            }
        }

    def test_path_traversal_is_rejected(self) -> None:
        result = self.call("read_file", {"path": "../secret.txt"})
        self.assertTrue(result.is_error)

    def test_submission_requires_fresh_passing_tests(self) -> None:
        self.assertTrue(self.call("submit_candidate", self.claim()).is_error)
        self.assertFalse(
            self.call("write_file", {"path": "solver.txt", "content": "new\n"}).is_error
        )
        self.assertFalse(self.call("run_public_tests", {}).is_error)
        self.assertFalse(self.call("submit_candidate", self.claim()).is_error)
        self.assertTrue(self.executor.submitted)

    def test_change_invalidates_previous_public_test(self) -> None:
        self.call("write_file", {"path": "solver.txt", "content": "new\n"})
        self.call("run_public_tests", {})
        self.call("write_file", {"path": "notes.txt", "content": "changed"})

        result = self.call("submit_candidate", self.claim())
        self.assertTrue(result.is_error)

    def test_failed_write_preserves_existing_file_and_test_status(self) -> None:
        self.call("write_file", {"path": "solver.txt", "content": "new\n"})
        self.call("run_public_tests", {})
        with patch("iah_arena.tools.os.replace", side_effect=OSError("disk error")):
            result = self.call("write_file", {"path": "solver.txt", "content": "broken"})

        self.assertTrue(result.is_error)
        self.assertEqual((self.workspace / "solver.txt").read_bytes(), b"new\n")
        self.assertTrue(self.executor.last_public_tests_passed)
        self.assertEqual(set(self.workspace.iterdir()), {self.workspace / "solver.txt"})

    def test_failed_new_file_write_leaves_no_file_or_staging_file(self) -> None:
        with patch("iah_arena.tools.os.replace", side_effect=OSError("disk error")):
            result = self.call("write_file", {"path": "extra.txt", "content": "new"})

        self.assertTrue(result.is_error)
        self.assertEqual(set(self.workspace.iterdir()), {self.workspace / "solver.txt"})

    def test_failed_staging_write_preserves_existing_file(self) -> None:
        original = (self.workspace / "solver.txt").read_bytes()
        real_temporary_file = tempfile.NamedTemporaryFile

        def failing_temporary_file(*args, **kwargs):
            temporary = real_temporary_file(*args, **kwargs)

            def partial_write(content):
                temporary.file.write(content[:1])
                raise OSError("disk full")

            temporary.write = partial_write
            return temporary

        with patch("iah_arena.tools.tempfile.NamedTemporaryFile", failing_temporary_file):
            result = self.call("write_file", {"path": "solver.txt", "content": "changed"})

        self.assertTrue(result.is_error)
        self.assertEqual((self.workspace / "solver.txt").read_bytes(), original)
        self.assertEqual(set(self.workspace.iterdir()), {self.workspace / "solver.txt"})

    def test_replace_text_uses_atomic_write(self) -> None:
        original = (self.workspace / "solver.txt").read_bytes()
        with patch("iah_arena.tools.os.replace", side_effect=OSError("disk error")):
            result = self.call(
                "replace_text", {"path": "solver.txt", "old": "old", "new": "new"}
            )

        self.assertTrue(result.is_error)
        self.assertEqual((self.workspace / "solver.txt").read_bytes(), original)
        result = self.call(
            "replace_text", {"path": "solver.txt", "old": "old", "new": "new"}
        )
        self.assertFalse(result.is_error)
        self.assertEqual((self.workspace / "solver.txt").read_bytes(), original.replace(b"old", b"new"))

    def test_write_preserves_exact_utf8_bytes(self) -> None:
        content = "\u043f\u0440\u0438\u0432\u0456\u0442\r\n\u03bb\n"
        encoded = content.encode("utf-8")
        result = self.call("write_file", {"path": "solver.txt", "content": content})

        self.assertFalse(result.is_error)
        self.assertEqual((self.workspace / "solver.txt").read_bytes(), encoded)
        self.assertEqual(result.output["bytes"], len(encoded))
        self.assertEqual(result.output["sha256"], hashlib.sha256(encoded).hexdigest())

    @unittest.skipIf(os.name == "nt", "POSIX executable mode is not supported on Windows")
    def test_write_preserves_executable_mode(self) -> None:
        path = self.workspace / "solver.txt"
        path.chmod(0o755)
        result = self.call("write_file", {"path": "solver.txt", "content": "new\n"})

        self.assertFalse(result.is_error)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o755)

    def test_stale_digest_rejects_all_mutations_and_allows_fresh_retry(self) -> None:
        for name, extra in (
            ("write_file", {"content": "overwrite"}),
            ("replace_text", {"old": "old", "new": "replacement"}),
            ("delete_file", {}),
        ):
            with self.subTest(tool=name):
                path = self.workspace / "solver.txt"
                path.write_bytes(b"old\n")
                stale = self.call("read_file", {"path": "solver.txt"}).output["sha256"]
                # Keep the replace_text target present: matching text alone is insufficient.
                self.call("write_file", {"path": "solver.txt", "content": "old\nadded\n"})
                self.executor.last_public_tests_passed = True
                result = self.call(name, {"path": "solver.txt", **extra, "expected_sha256": stale})
                self.assertTrue(result.is_error)
                self.assertIn("read_file", result.output["error"])
                self.assertEqual(path.read_bytes(), b"old\nadded\n")
                self.assertTrue(self.executor.last_public_tests_passed)
                self.assertEqual(set(self.workspace.iterdir()), {path})

                fresh = self.call("read_file", {"path": "solver.txt"}).output["sha256"]
                result = self.call(name, {"path": "solver.txt", **extra, "expected_sha256": fresh})
                self.assertFalse(result.is_error)
                self.assertFalse(self.executor.last_public_tests_passed)
                if name == "delete_file":
                    self.assertFalse(path.exists())
                else:
                    expected = b"overwrite" if name == "write_file" else b"replacement\nadded\n"
                    self.assertEqual(path.read_bytes(), expected)

    def test_create_requires_absent_path_and_cannot_overwrite(self) -> None:
        arguments = {"path": "created.txt", "content": "created", "expected_sha256": None}
        self.assertFalse(self.call("write_file", arguments).is_error)
        arguments["content"] = "overwrite"
        self.assertTrue(self.call("write_file", arguments).is_error)
        self.assertEqual((self.workspace / "created.txt").read_bytes(), b"created")

    def test_missing_or_invalid_digest_is_rejected(self) -> None:
        original = (self.workspace / "solver.txt").read_bytes()
        for name, extra in (
            ("write_file", {"content": "changed"}),
            ("replace_text", {"old": "old", "new": "changed"}),
            ("delete_file", {}),
        ):
            for value in ("missing", None, "", "g" * 64, "a" * 63, 123, []):
                with self.subTest(tool=name, digest=value):
                    arguments = {"path": "solver.txt", **extra}
                    if value != "missing":
                        arguments["expected_sha256"] = value
                    result = self.executor.execute(ToolCall("invalid", name, arguments))
                    self.assertTrue(result.is_error)
                    self.assertEqual((self.workspace / "solver.txt").read_bytes(), original)

    def test_deleted_file_cannot_be_recreated_with_stale_digest(self) -> None:
        digest = self.call("read_file", {"path": "solver.txt"}).output["sha256"]
        self.call("delete_file", {"path": "solver.txt", "expected_sha256": digest})
        result = self.call("write_file", {
            "path": "solver.txt", "content": "resurrected", "expected_sha256": digest,
        })
        self.assertTrue(result.is_error)
        self.assertFalse((self.workspace / "solver.txt").exists())

    def test_read_hash_and_edits_preserve_exact_newlines(self) -> None:
        data = "\u03bb\r\nold\r\n".encode("utf-8")
        path = self.workspace / "solver.txt"
        path.write_bytes(data)
        read = self.call("read_file", {"path": "solver.txt"})
        self.assertEqual(read.output["content"].encode("utf-8"), data)
        self.assertEqual(read.output["sha256"], hashlib.sha256(data).hexdigest())
        edited = self.call("replace_text", {
            "path": "solver.txt", "old": "old", "new": "new",
            "expected_sha256": read.output["sha256"],
        })
        self.assertFalse(edited.is_error)
        self.assertEqual(path.read_bytes(), data.replace(b"old", b"new"))
        self.assertEqual(edited.output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertFalse(self.call("delete_file", {
            "path": "solver.txt", "expected_sha256": edited.output["sha256"],
        }).is_error)


if __name__ == "__main__":
    unittest.main()
