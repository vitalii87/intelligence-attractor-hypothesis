"""Experimental writable agent package launcher; not wired into iterate yet."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile

from .runtime import Mount, RuntimeRequest, RuntimeRole


def inspect_package(directory: Path) -> dict:
    directory = Path(directory)
    if directory.is_symlink() or getattr(directory, "is_junction", lambda: False)() or not directory.is_dir():
        raise ValueError("package must be a regular directory")
    files = {}
    total = 0
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("package links are not allowed")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("package contains a special file")
        size = path.stat().st_size
        total += size
        if size > 256000 or total > 2000000 or len(files) >= 256:
            raise ValueError("package exceeds prototype file limits")
        files[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((directory / "agent.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "argv"} or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("invalid agent manifest")
    argv = manifest["argv"]
    if not isinstance(argv, list) or not 1 <= len(argv) <= 32 or any(not isinstance(a, str) or not a or len(a) > 4096 or "\0" in a for a in argv):
        raise ValueError("invalid entry command")
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"argv": argv, "files": files, "bytes": total, "sha256": digest}


def run_package(directory, runtime, limits, task_text: str):
    """Run a disposable WORKING COPY. No automatic promotion or host execution."""
    if not isinstance(task_text, str) or not task_text.strip() or len(task_text) > 30000:
        raise ValueError("bounded author task text required")
    before = inspect_package(directory)
    passport = {
        "contract": "agent-package-v1", "task": task_text,
        "instruction": "Work toward the task within the declared limits. You control the writable workspace. Preserve the external entry contract.",
        "workspace": {"path": "/workspace", "writable": True,
                      "files": list(before["files"]), "bytes": before["bytes"],
                      "size_check": "validated before and after launch; not a live disk quota", "max_files": 256, "max_file_bytes": 256000, "max_package_bytes": 2000000},
        "entry": {"manifest": "agent.json", "argv": before["argv"],
                  "context_argument": "/arena-context/context.json",
                  "reload": "agent.json is read afresh on each launch"},
        "runtime_limits": asdict(limits),
        "capabilities": {"network": False, "model_gateway": False,
                         "credentials": False, "other_workspaces": False},
        "persistence": "Files in this working copy survive launches; temporary container storage does not. Promotion is external.",
        "accounting": "This prototype does not enforce cumulative token budgets or iteration scheduling; model calls are unavailable.",
    }
    with tempfile.TemporaryDirectory(prefix="iah-context-") as temporary:
        context_dir = Path(temporary)
        (context_dir / "context.json").write_text(json.dumps(passport), encoding="utf-8")
        request = RuntimeRequest(tuple(before["argv"]) + ("/arena-context/context.json",),
                                 RuntimeRole.WORKSHOP, workspace_read_only=False,
                                 extra_mounts=(Mount(context_dir, "/arena-context", True),))
        result = runtime.run(Path(directory), request, limits)
    after = None
    try:
        after = inspect_package(directory)
    except (OSError, ValueError):
        pass
    return {"before": before, "after": after, "package_valid": after is not None,
            "runtime": result.as_dict(), "passport": passport,
            "changed": after is None or before["sha256"] != after["sha256"]}
