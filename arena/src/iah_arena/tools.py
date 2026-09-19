from __future__ import annotations

import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

from .prompts import ImprovementClaim
from .providers import ToolCall, ToolDefinition, ToolResult


class ToolExecutionError(RuntimeError):
    pass


@dataclass
class EditBudget:
    max_bytes: int
    max_operations: int
    bytes_used: int = 0
    operations_used: int = 0

    def check(self, size: int) -> None:
        if self.bytes_used + size > self.max_bytes or self.operations_used + 1 > self.max_operations:
            raise ToolExecutionError("edit budget exhausted")

    def charge(self, size: int) -> None:
        self.bytes_used += size
        self.operations_used += 1


PublicTestRunner = Callable[[Path], Mapping[str, Any]]


CANONICAL_TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        name="list_files",
        description="List regular files in the mutable candidate workspace.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    ToolDefinition(
        name="read_file",
        description="Read one UTF-8 text file from the candidate workspace.",
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="write_file",
        description="Create or replace a UTF-8 file. Supply its latest sha256; null requires a new path.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "expected_sha256": {"type": ["string", "null"]},
            },
            "required": ["path", "content", "expected_sha256"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="replace_text",
        description="Replace one exact text occurrence, only if the file matches its latest sha256.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old": {"type": "string"},
                "new": {"type": "string"},
                "expected_sha256": {"type": "string"},
            },
            "required": ["path", "old", "new", "expected_sha256"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="delete_file",
        description="Delete a regular workspace file only if it matches its latest sha256.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "expected_sha256": {"type": "string"},
            },
            "required": ["path", "expected_sha256"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="run_public_tests",
        description="Run the arena-controlled public test suite and return structured results.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    ToolDefinition(
        name="submit_candidate",
        description="Submit the tested transactional workspace for independent evaluation.",
        input_schema={
            "type": "object",
            "properties": {
                "claim": {
                    "type": "object",
                    "properties": {
                        "bottleneck": {"type": "string"},
                        "hypothesis": {"type": "string"},
                        "changes": {"type": "array", "items": {"type": "string"}},
                        "expected_effect": {"type": "string"},
                        "risks": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "bottleneck",
                        "hypothesis",
                        "changes",
                        "expected_effect",
                        "risks",
                    ],
                    "additionalProperties": False,
                }
            },
            "required": ["claim"],
            "additionalProperties": False,
        },
    ),
    ToolDefinition(
        name="abort_attempt",
        description="End the current attempt without submitting a candidate.",
        input_schema={
            "type": "object",
            "properties": {"reason": {"type": "string"}},
            "required": ["reason"],
            "additionalProperties": False,
        },
    ),
)


class WorkspaceToolExecutor:
    def __init__(
        self,
        workspace: Path,
        *,
        public_test_runner: PublicTestRunner,
        max_file_bytes: int = 256_000,
        max_workspace_bytes: int = 2_000_000,
        edit_budget: EditBudget | None = None,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.public_test_runner = public_test_runner
        self.max_file_bytes = max_file_bytes
        self.max_workspace_bytes = max_workspace_bytes
        self.edit_budget = edit_budget
        self.last_public_tests_passed = False
        self.submitted = False
        self.aborted = False
        self.terminal_reason: str | None = None
        self.submission_claim: ImprovementClaim | None = None

    def execute(self, call: ToolCall) -> ToolResult:
        if self.submitted or self.aborted:
            return ToolResult(call.call_id, {"error": "attempt is already terminal"}, is_error=True)
        try:
            handler = getattr(self, f"_tool_{call.name}")
        except AttributeError:
            return ToolResult(call.call_id, {"error": f"unknown tool: {call.name}"}, is_error=True)
        try:
            output = handler(call.arguments)
            return ToolResult(call.call_id, dict(output))
        except (KeyError, OSError, UnicodeError, ValueError, ToolExecutionError) as error:
            return ToolResult(call.call_id, {"error": str(error)}, is_error=True)

    def _tool_list_files(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, set())
        files = []
        for path in sorted(self.workspace.rglob("*")):
            if path.is_symlink():
                raise ToolExecutionError("workspace contains a symlink")
            if path.is_file():
                files.append(path.relative_to(self.workspace).as_posix())
        return {"files": files}

    def _tool_read_file(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"path"})
        path = self._resolve_file(str(arguments["path"]), must_exist=True)
        if path.stat().st_size > self.max_file_bytes:
            raise ToolExecutionError("file exceeds read limit")
        data = path.read_bytes()
        content = data.decode("utf-8")
        return {
            "path": path.relative_to(self.workspace).as_posix(),
            "content": content,
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    def _tool_write_file(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"path", "content", "expected_sha256"})
        content = str(arguments["content"])
        encoded = content.encode("utf-8")
        if len(encoded) > self.max_file_bytes:
            raise ToolExecutionError("file exceeds write limit")
        path = self._resolve_file(str(arguments["path"]), must_exist=False)
        self._check_expected_hash(path, arguments["expected_sha256"], allow_missing=True)
        existing_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
        existing_size = path.stat().st_size if path.exists() else 0
        projected = self._workspace_size() - existing_size + len(encoded)
        if projected > self.max_workspace_bytes:
            raise ToolExecutionError("workspace exceeds size limit")
        if self.edit_budget is not None:
            self.edit_budget.check(len(encoded))
        path.parent.mkdir(parents=True, exist_ok=True)
        # Stage beside the destination so replacement stays on one filesystem.
        # A failed write must never truncate the agent's current source file.
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=path.parent, prefix=".iah-write-", delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(encoded)
            if existing_mode is not None:
                temporary_path.chmod(existing_mode)
            os.replace(temporary_path, path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        self.last_public_tests_passed = False
        if self.edit_budget is not None:
            self.edit_budget.charge(len(encoded))
        return {
            "path": path.relative_to(self.workspace).as_posix(),
            "bytes": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }

    def _tool_replace_text(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"path", "old", "new", "expected_sha256"})
        path = self._resolve_file(str(arguments["path"]), must_exist=True)
        data = self._check_expected_hash(path, arguments["expected_sha256"])
        old = str(arguments["old"])
        new = str(arguments["new"])
        if not old:
            raise ToolExecutionError("old text must not be empty")
        content = data.decode("utf-8")
        occurrences = content.count(old)
        if occurrences != 1:
            raise ToolExecutionError(f"expected one occurrence, found {occurrences}")
        return self._tool_write_file(
            {
                "path": arguments["path"],
                "content": content.replace(old, new),
                "expected_sha256": arguments["expected_sha256"],
            }
        )

    def _tool_delete_file(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"path", "expected_sha256"})
        path = self._resolve_file(str(arguments["path"]), must_exist=True)
        self._check_expected_hash(path, arguments["expected_sha256"])
        size = path.stat().st_size
        if self.edit_budget is not None:
            self.edit_budget.check(size)
        path.unlink()
        if self.edit_budget is not None:
            self.edit_budget.charge(size)
        self.last_public_tests_passed = False
        return {"path": path.relative_to(self.workspace).as_posix(), "deleted": True}

    def _check_expected_hash(
        self, path: Path, expected: Any, *, allow_missing: bool = False
    ) -> bytes:
        if expected is None:
            if not allow_missing:
                raise ToolExecutionError("expected_sha256 must be a SHA-256 hex digest")
            if path.exists() or path.is_symlink():
                raise ToolExecutionError("file already exists; read_file before editing it")
            return b""
        if (
            not isinstance(expected, str)
            or len(expected) != 64
            or any(character not in "0123456789abcdef" for character in expected)
        ):
            raise ToolExecutionError("expected_sha256 must be a lowercase SHA-256 hex digest")
        if not path.is_file():
            raise ToolExecutionError("file no longer exists; refresh the workspace before editing")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ToolExecutionError("file changed; use read_file and retry with its latest sha256")
        return data

    def _tool_run_public_tests(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, set())
        result = dict(self.public_test_runner(self.workspace))
        passed = result.get("passed")
        if not isinstance(passed, bool):
            raise ToolExecutionError("public test result must contain boolean 'passed'")
        self.last_public_tests_passed = passed
        return result

    def _tool_submit_candidate(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"claim"})
        if not self.last_public_tests_passed:
            raise ToolExecutionError("public tests must pass after the last workspace change")
        claim_value = arguments["claim"]
        if not isinstance(claim_value, Mapping):
            raise ToolExecutionError("claim must be an object")
        claim = ImprovementClaim.from_mapping(claim_value)
        self.submitted = True
        self.submission_claim = claim
        self.terminal_reason = f"{claim.bottleneck}: {claim.hypothesis}"
        return {"submitted": True, "claim": claim.as_dict()}

    def _tool_abort_attempt(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_keys(arguments, {"reason"})
        self.aborted = True
        self.terminal_reason = str(arguments["reason"])
        return {"aborted": True, "reason": self.terminal_reason}

    def _resolve_file(self, value: str, *, must_exist: bool) -> Path:
        normalized = value.replace("\\", "/")
        relative = PurePosixPath(normalized)
        if relative.is_absolute() or not relative.parts:
            raise ToolExecutionError("path must be relative")
        if any(
            part in {"", ".", "..", ".git"} or ":" in part
            for part in relative.parts
        ):
            raise ToolExecutionError("path contains a forbidden component")
        candidate = self.workspace.joinpath(*relative.parts)
        resolved_parent = candidate.parent.resolve()
        if not resolved_parent.is_relative_to(self.workspace):
            raise ToolExecutionError("path escapes the workspace")
        current = self.workspace
        for part in relative.parts[:-1]:
            current = current / part
            if current.exists() and current.is_symlink():
                raise ToolExecutionError("symlink traversal is forbidden")
        if candidate.exists() and candidate.is_symlink():
            raise ToolExecutionError("symlink files are forbidden")
        if must_exist and not candidate.is_file():
            raise FileNotFoundError(value)
        if not must_exist and candidate.exists() and not candidate.is_file():
            raise ToolExecutionError("path is not a regular file")
        return candidate

    def _workspace_size(self) -> int:
        total = 0
        for path in self.workspace.rglob("*"):
            if path.is_symlink():
                raise ToolExecutionError("workspace contains a symlink")
            if path.is_file():
                total += path.stat().st_size
        return total

    @staticmethod
    def _require_keys(arguments: Mapping[str, Any], expected: set[str]) -> None:
        actual = set(arguments)
        if actual != expected:
            raise ToolExecutionError(
                f"invalid arguments; expected {sorted(expected)}, received {sorted(actual)}"
            )
