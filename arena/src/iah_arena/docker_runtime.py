from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence
from uuid import uuid4

from .runtime import CandidateRuntime, Mount, RuntimeLimits, RuntimeRequest, RuntimeResult


_DIGEST_IMAGE = re.compile(r"^(?:.+@sha256:|sha256:)[0-9a-fA-F]{64}$")


class DockerRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


ProcessRunner = Callable[[Sequence[str], float], ProcessResult]


def _default_process_runner(argv: Sequence[str], timeout: float) -> ProcessResult:
    completed = subprocess.run(
        list(argv),
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        shell=False,
        timeout=timeout,
    )
    return ProcessResult(completed.returncode, completed.stdout, completed.stderr)


class DockerRuntime(CandidateRuntime):
    """A no-network, least-privilege Docker execution boundary."""

    def __init__(
        self,
        image: str,
        *,
        docker_binary: str = "docker",
        container_user: str = "1000:1000",
        process_runner: ProcessRunner = _default_process_runner,
        require_digest: bool = True,
    ) -> None:
        if require_digest and not _DIGEST_IMAGE.fullmatch(image):
            raise ValueError("Docker image must be a registry digest or local sha256 image ID")
        if not image.strip() or not docker_binary.strip() or not container_user.strip():
            raise ValueError("image, docker_binary, and container_user must not be empty")
        self.image = image
        self.docker_binary = docker_binary
        self.container_user = container_user
        self.process_runner = process_runner

    def check_ready(self) -> None:
        """Check Linux engine and a locally available pinned image before a run.

        Never pull implicitly here: experiment setup and evaluation are separate.
        This is a prerequisite check, not a substitute for a container smoke test.
        """
        checks = (
            ((self.docker_binary, "info", "--format", "{{.OSType}}"), "Linux engine"),
            ((self.docker_binary, "image", "inspect", "--format", "{{.Os}}", self.image), "pinned local image"),
        )
        for command, label in checks:
            try:
                result = self.process_runner(command, 10.0)
            except (OSError, subprocess.TimeoutExpired) as error:
                raise DockerRuntimeError(f"Docker {label} check failed: {error}") from error
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()[:2000]
                raise DockerRuntimeError(f"Docker {label} unavailable: {detail}")
            if result.stdout.strip() != "linux":
                raise DockerRuntimeError(f"Docker {label} must use Linux containers")

    def run(
        self,
        workspace: Path,
        request: RuntimeRequest,
        limits: RuntimeLimits,
    ) -> RuntimeResult:
        workspace = Path(workspace).resolve()
        if not workspace.is_dir():
            raise FileNotFoundError(f"workspace not found: {workspace}")
        name = f"iah-{request.role.value}-{uuid4().hex[:12]}"
        argv = self.build_command(workspace, request, limits, container_name=name)
        started = time.monotonic()
        try:
            completed = self.process_runner(argv, limits.timeout_seconds)
            if completed.returncode in {125, 126, 127}:
                detail = (completed.stderr or completed.stdout).strip()[:2000]
                raise DockerRuntimeError(
                    f"Docker launch failed (exit {completed.returncode}): {detail}"
                )
            elapsed_ms = max(0, round((time.monotonic() - started) * 1000))
            stdout, stderr, truncated = self._bounded_output(
                completed.stdout,
                completed.stderr,
                limits.max_output_bytes,
            )
            return RuntimeResult(
                exit_code=completed.returncode,
                timed_out=False,
                duration_ms=elapsed_ms,
                stdout=stdout,
                stderr=stderr,
                output_truncated=truncated,
                runtime_metadata={
                    "engine": "docker",
                    "image": self.image,
                    "role": request.role.value,
                },
            )
        except subprocess.TimeoutExpired as error:
            self._force_remove(name)
            elapsed_ms = max(0, round((time.monotonic() - started) * 1000))
            stdout, stderr, truncated = self._bounded_output(
                self._decode_timeout_output(error.stdout),
                self._decode_timeout_output(error.stderr),
                limits.max_output_bytes,
            )
            return RuntimeResult(
                exit_code=None,
                timed_out=True,
                duration_ms=elapsed_ms,
                stdout=stdout,
                stderr=stderr,
                output_truncated=truncated,
                runtime_metadata={
                    "engine": "docker",
                    "image": self.image,
                    "role": request.role.value,
                },
            )

    def build_command(
        self,
        workspace: Path,
        request: RuntimeRequest,
        limits: RuntimeLimits,
        *,
        container_name: str,
    ) -> list[str]:
        workspace = Path(workspace).resolve()
        argv = [
            self.docker_binary,
            "run",
            "--rm",
            "--init",
            "--name",
            container_name,
            "--network",
            "none",
            "--cpus",
            str(limits.cpus),
            "--memory",
            f"{limits.memory_mb}m",
            "--memory-swap",
            f"{limits.memory_mb}m",
            "--pids-limit",
            str(limits.pids),
            "--ulimit",
            "nofile=1024:1024",
            "--ulimit",
            "core=0:0",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--user",
            self.container_user,
            "--env",
            "HOME=/tmp/home",
            "--env",
            "XDG_CACHE_HOME=/tmp/cache",
            "--env",
            "CARGO_HOME=/tmp/cargo",
            "--env",
            "GOCACHE=/tmp/go-cache",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,nodev,size={limits.tmpfs_mb}m",
            "--tmpfs",
            f"/run/iah:rw,exec,nosuid,nodev,size={limits.tmpfs_mb}m",
            "--mount",
            self._mount_value(Mount(workspace, "/workspace", request.workspace_read_only)),
            "--workdir",
            request.working_directory,
        ]
        targets = {"/workspace"}
        for mount in request.extra_mounts:
            host = Path(mount.host_path).resolve()
            if not host.exists():
                raise FileNotFoundError(f"mount source not found: {host}")
            if mount.container_path in targets:
                raise ValueError(f"duplicate container mount path: {mount.container_path}")
            targets.add(mount.container_path)
            argv.extend(
                (
                    "--mount",
                    self._mount_value(Mount(host, mount.container_path, mount.read_only)),
                )
            )
        argv.extend((self.image, *request.argv))
        return argv

    @staticmethod
    def _mount_value(mount: Mount) -> str:
        source = str(Path(mount.host_path).resolve())
        if "," in source or "," in mount.container_path:
            raise ValueError("Docker mount paths must not contain commas")
        mode = "readonly" if mount.read_only else "rw"
        return f"type=bind,source={source},target={mount.container_path},{mode}"

    def _force_remove(self, container_name: str) -> None:
        try:
            self.process_runner(
                (self.docker_binary, "rm", "--force", container_name),
                10.0,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    @staticmethod
    def _decode_timeout_output(value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    @staticmethod
    def _bounded_output(stdout: str, stderr: str, limit: int) -> tuple[str, str, bool]:
        stdout_bytes = stdout.encode("utf-8")
        stderr_bytes = stderr.encode("utf-8")
        if len(stdout_bytes) + len(stderr_bytes) <= limit:
            return stdout, stderr, False
        stdout_limit = limit // 2
        stderr_limit = limit - stdout_limit
        bounded_stdout = stdout_bytes[:stdout_limit].decode("utf-8", errors="ignore")
        bounded_stderr = stderr_bytes[:stderr_limit].decode("utf-8", errors="ignore")
        return bounded_stdout, bounded_stderr, True
