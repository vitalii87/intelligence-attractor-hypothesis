"""Isolated package attempts, using the existing accepted-generation store."""
from pathlib import Path

from .agent_package import inspect_package, run_package
from .locking import FileLock
from .workspace import LineageWorkspaceManager, _write_json_atomic


class PackageAttempts:
    def __init__(self, state_dir: Path, lineage_id: str):
        self.manager = LineageWorkspaceManager(state_dir, lineage_id)
        self.lock = self.manager.root / ".package.lock"

    def initialize(self, seed: Path):
        with FileLock(self.lock):
            inspect_package(seed)
            current = self.manager.initialize(seed)
            _write_json_atomic(current.parent / "package.json", inspect_package(current))
            return current

    def run(self, *, epoch: int, attempt: int, runtime, limits, task_text: str, evaluator):
        """Evaluator is trusted controller code, never a candidate-supplied command.

        It receives the completed working copy and must return a dict containing
        boolean accepted and string reason. It must not mutate the package.
        """
        if any(type(n) is not int or n < 1 for n in (epoch, attempt)):
            raise ValueError("epoch and attempt must be positive integers")
        with FileLock(self.lock):
            current = self.manager.current_files()
            before = inspect_package(current)
            import json
            expected = json.loads((current.parent / "package.json").read_text())["sha256"]
            if before["sha256"] != expected:
                raise ValueError("accepted package changed outside controller")
            workspace = self.manager.begin_attempt(epoch=epoch, attempt=attempt)
            # Record intent before executing; interrupted work is never auto-promoted.
            _write_json_atomic(workspace.path / "package-run.json", {
                "status": "started", "parent_sha256": before["sha256"], "task_text": task_text,
            })
            try:
                report = run_package(workspace.files_path, runtime, limits, task_text)
                _write_json_atomic(workspace.path / "package-run.json", {"status": "executed", **report})
                outcome = report["runtime"]
                if not report["package_valid"] or outcome["exit_code"] != 0 or outcome["timed_out"] or outcome["output_truncated"]:
                    decision = {"accepted": False, "reason": "execution or package validation failed"}
                else:
                    decision = evaluator(workspace.files_path)
                    if not isinstance(decision, dict) or type(decision.get("accepted")) is not bool or not isinstance(decision.get("reason"), str):
                        raise ValueError("invalid trusted evaluator decision")
                    if inspect_package(workspace.files_path)["sha256"] != report["after"]["sha256"]:
                        raise ValueError("evaluator mutated candidate package")
                # Candidate mount must never expose accepted generations.
                if inspect_package(current)["sha256"] != before["sha256"]:
                    raise ValueError("accepted package changed during attempt")
                _write_json_atomic(workspace.path / "decision.json", decision)
            except Exception as error:
                # Keep working files for inspection, but do not persist exception
                # text that a transport/evaluator might populate with credentials.
                _write_json_atomic(workspace.path / "failure.json", {"type": type(error).__name__})
                self.manager.reject(workspace, reason="package attempt failed")
                raise
            if decision["accepted"]:
                _write_json_atomic(workspace.path / "package.json", report["after"])
                workspace = self.manager.submit(workspace)
                terminal = self.manager.accept(workspace)
            else:
                terminal = self.manager.reject(workspace, reason=decision["reason"])
            return {"accepted": decision["accepted"], "reason": decision["reason"],
                    "generation": self.manager.current_generation(), "path": str(terminal.path),
                    "package": report}
