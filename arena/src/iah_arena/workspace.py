from __future__ import annotations

import json
import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .lifecycle import AttemptLifecycle, AttemptStatus


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _move_directory(source: Path, target: Path) -> None:
    # Windows scanners can briefly hold a newly written candidate directory.
    # Retry only access failures, never delete or fall back to partial copying.
    for attempt in range(5):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if os.name != "nt" or attempt == 4:
                raise
            time.sleep(0.05 * 2**attempt)


class WorkspaceError(RuntimeError):
    pass


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


@dataclass(frozen=True, slots=True)
class AttemptWorkspace:
    path: Path
    files_path: Path
    lifecycle: AttemptLifecycle


class LineageWorkspaceManager:
    """Content-preserving accepted generations and transactional attempts."""

    def __init__(self, state_dir: Path, lineage_id: str) -> None:
        if not _SAFE_ID.fullmatch(lineage_id):
            raise ValueError("lineage_id contains unsupported characters")
        self.lineage_id = lineage_id
        self.root = Path(state_dir) / "lineages" / lineage_id / "workspace"
        self.accepted_root = self.root / "accepted"
        self.attempts_root = self.root / "attempts"
        self.rejected_root = self.root / "rejected"
        self.state_path = self.root / "state.json"

    def initialize(self, seed_workspace: Path) -> Path:
        if self.state_path.exists():
            raise FileExistsError(f"workspace already exists: {self.lineage_id}")
        seed_workspace = Path(seed_workspace)
        if not seed_workspace.is_dir():
            raise FileNotFoundError(f"seed workspace not found: {seed_workspace}")
        if any(path.is_symlink() for path in seed_workspace.rglob("*")):
            raise WorkspaceError("seed workspace must not contain symlinks")

        generation_dir = self.accepted_root / "gen-0000"
        files_path = generation_dir / "files"
        files_path.parent.mkdir(parents=True, exist_ok=False)
        shutil.copytree(seed_workspace, files_path)
        _write_json_atomic(
            generation_dir / "generation.json",
            {"generation": 0, "source": "seed"},
        )
        _write_json_atomic(
            self.state_path,
            {"generation": 0, "accepted": "accepted/gen-0000"},
        )
        return files_path

    def current_generation(self) -> int:
        return int(self._read_state()["generation"])

    def current_files(self) -> Path:
        state = self._read_state()
        generation_dir = self.root / str(state["accepted"])
        files = generation_dir / "files"
        if not files.is_dir():
            raise WorkspaceError("accepted workspace is missing")
        return files

    def begin_attempt(self, *, epoch: int, attempt: int) -> AttemptWorkspace:
        parent_generation = self.current_generation()
        name = f"epoch-{epoch:04d}-attempt-{attempt:04d}"
        path = self.attempts_root / name
        files_path = path / "files"
        if path.exists() or (self.rejected_root / name).exists():
            raise FileExistsError(f"attempt already exists: {name}")
        files_path.parent.mkdir(parents=True, exist_ok=False)
        shutil.copytree(self.current_files(), files_path)
        lifecycle = AttemptLifecycle(
            epoch=epoch,
            attempt=attempt,
            parent_generation=parent_generation,
        )
        self._write_lifecycle(path, lifecycle)
        return AttemptWorkspace(path, files_path, lifecycle)

    def load_attempt(self, *, epoch: int, attempt: int) -> AttemptWorkspace:
        name = f"epoch-{epoch:04d}-attempt-{attempt:04d}"
        for parent in (self.attempts_root, self.rejected_root):
            path = parent / name
            if (path / "attempt.json").exists():
                lifecycle = AttemptLifecycle.from_dict(self._read_json(path / "attempt.json"))
                return AttemptWorkspace(path, path / "files", lifecycle)
        raise FileNotFoundError(f"attempt not found: {name}")

    def submit(self, workspace: AttemptWorkspace) -> AttemptWorkspace:
        return self._transition(workspace, AttemptStatus.SUBMITTED)

    def accept(self, workspace: AttemptWorkspace) -> AttemptWorkspace:
        lifecycle = workspace.lifecycle.transition(AttemptStatus.ACCEPTED)
        next_generation = lifecycle.parent_generation + 1
        target = self.accepted_root / f"gen-{next_generation:04d}"
        if target.exists():
            raise FileExistsError(f"accepted generation already exists: {next_generation}")
        self._write_lifecycle(workspace.path, lifecycle)
        target.parent.mkdir(parents=True, exist_ok=True)
        _move_directory(workspace.path, target)
        _write_json_atomic(
            target / "generation.json",
            {
                "generation": next_generation,
                "parent_generation": lifecycle.parent_generation,
                "epoch": lifecycle.epoch,
                "attempt": lifecycle.attempt,
            },
        )
        _write_json_atomic(
            self.state_path,
            {"generation": next_generation, "accepted": f"accepted/gen-{next_generation:04d}"},
        )
        return AttemptWorkspace(target, target / "files", lifecycle)

    def reject(self, workspace: AttemptWorkspace, *, reason: str) -> AttemptWorkspace:
        return self._archive_terminal(workspace, AttemptStatus.REJECTED, reason)

    def abort(self, workspace: AttemptWorkspace, *, reason: str) -> AttemptWorkspace:
        return self._archive_terminal(workspace, AttemptStatus.ABORTED, reason)

    def _archive_terminal(
        self,
        workspace: AttemptWorkspace,
        status: AttemptStatus,
        reason: str,
    ) -> AttemptWorkspace:
        lifecycle = workspace.lifecycle.transition(status, reason=reason)
        self._write_lifecycle(workspace.path, lifecycle)
        target = self.rejected_root / workspace.path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(f"archived attempt already exists: {target.name}")
        _move_directory(workspace.path, target)
        return AttemptWorkspace(target, target / "files", lifecycle)

    def _transition(
        self,
        workspace: AttemptWorkspace,
        target: AttemptStatus,
        *,
        reason: str | None = None,
    ) -> AttemptWorkspace:
        lifecycle = workspace.lifecycle.transition(target, reason=reason)
        self._write_lifecycle(workspace.path, lifecycle)
        return AttemptWorkspace(workspace.path, workspace.files_path, lifecycle)

    def _read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            raise WorkspaceError(f"workspace is not initialized: {self.lineage_id}")
        return self._read_json(self.state_path)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise WorkspaceError(f"expected JSON object: {path}")
        return value

    @staticmethod
    def _write_lifecycle(path: Path, lifecycle: AttemptLifecycle) -> None:
        _write_json_atomic(path / "attempt.json", lifecycle.as_dict())
