"""Read-only verifier for explicit Arena ArtifactStore v1 directories."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat

from ..models import ArtifactRef, EntityVersion


class ImportFailure(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ImportFailure("duplicate JSON key")
        result[key] = value
    return result


def _regular(path, *, directory=False):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ImportFailure("links and reparse points are not allowed")
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise ImportFailure("unexpected file type")


def _read(path, maximum):
    _regular(path)
    if path.stat().st_size > maximum:
        raise ImportFailure("file size limit exceeded")
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ImportFailure("file size limit exceeded")
    return raw


@dataclass(frozen=True)
class ImportedArtifact:
    entity: EntityVersion
    manifest: ArtifactRef
    tree_sha256: str
    provenance_json: str


class ArenaArtifactAdapter:
    adapter_id = "arena-artifact-store"
    adapter_version = "1"
    max_file_bytes = 8_000_000
    max_total_bytes = 64_000_000
    max_entries = 4096

    def __init__(self, run_id: str):
        if not isinstance(run_id, str) or not run_id.strip():
            raise ImportFailure("explicit run ID required")
        self.run_id = run_id

    def load(self, source: Path) -> tuple[EntityVersion, ...]:
        return (self.inspect(source).entity,)

    def inspect(self, source: Path) -> ImportedArtifact:
        source = Path(os.path.abspath(source))
        # Refuse links in ancestors too; don't resolve them before checking.
        for parent in reversed((source, *source.parents)):
            _regular(parent, directory=True)
        raw = _read(source / "manifest.json", 2_000_000)
        try:
            manifest = json.loads(raw, object_pairs_hook=_object,
                                  parse_constant=lambda _: (_ for _ in ()).throw(ImportFailure("nonfinite JSON")))
        except (ValueError, RecursionError) as error:
            raise ImportFailure("invalid manifest JSON") from error
        required = {"schema_version", "artifact_id", "artifact_type", "tree_sha256", "files", "provenance", "created_utc"}
        if not isinstance(manifest, dict) or set(manifest) != required or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
            raise ImportFailure("unsupported manifest schema")
        files = manifest["files"]
        if not isinstance(files, list) or len(files) > self.max_entries:
            raise ImportFailure("invalid file inventory")
        expected, folded = {}, set()
        for item in files:
            if not isinstance(item, dict) or set(item) != {"path", "size_bytes", "sha256"}:
                raise ImportFailure("invalid file record")
            name = item["path"]
            if not isinstance(name, str) or any(c in name for c in ("\\", ":", "\0")) or any(p in ("", ".", "..") or p.endswith((".", " ")) for p in name.split("/")):
                raise ImportFailure("unsafe artifact path")
            if name.casefold() in folded:
                raise ImportFailure("duplicate or case-colliding path")
            folded.add(name.casefold())
            if type(item["size_bytes"]) is not int or not 0 <= item["size_bytes"] <= self.max_file_bytes:
                raise ImportFailure("invalid file size")
            ArtifactRef(name, item["sha256"])
            expected[name] = item
        if sum(item["size_bytes"] for item in files) > self.max_total_bytes:
            raise ImportFailure("total size limit exceeded")
        if digest(canonical(files)) != manifest["tree_sha256"]:
            raise ImportFailure("tree digest mismatch")
        identity = {key: manifest[key] for key in ("schema_version", "artifact_type", "tree_sha256", "files", "provenance")}
        if digest(canonical(identity)) != manifest["artifact_id"]:
            raise ImportFailure("artifact identity mismatch")
        provenance = manifest["provenance"]
        if not isinstance(provenance, dict) or not isinstance(provenance.get("lineage_id"), str) or not provenance["lineage_id"]:
            raise ImportFailure("missing lineage provenance")
        root = source / "files"
        _regular(root, directory=True)
        pending, actual, entries, total = [root], {}, 0, 0
        while pending:
            folder = pending.pop()
            with os.scandir(folder) as listing:
                for entry in listing:
                    entries += 1
                    if entries > self.max_entries:
                        raise ImportFailure("entry count limit exceeded")
                    path = Path(entry.path)
                    is_dir = entry.is_dir(follow_symlinks=False)
                    _regular(path, directory=is_dir)
                    if is_dir:
                        pending.append(path)
                        continue
                    name = path.relative_to(root).as_posix()
                    if name not in expected:
                        raise ImportFailure("unlisted artifact file")
                    data = _read(path, self.max_file_bytes)
                    total += len(data)
                    if total > self.max_total_bytes:
                        raise ImportFailure("total size limit exceeded")
                    if len(data) != expected[name]["size_bytes"] or digest(data) != expected[name]["sha256"]:
                        raise ImportFailure("artifact content mismatch")
                    actual[name] = ArtifactRef(str(path), digest(data))
        if set(actual) != set(expected):
            raise ImportFailure("missing artifact files")
        # Parent-generation integers are not immutable version IDs; do not invent a link.
        entity = EntityVersion(json.dumps([self.run_id, provenance["lineage_id"]]), manifest["artifact_id"],
                               tuple(actual[name] for name in sorted(actual)))
        return ImportedArtifact(entity, ArtifactRef(str(source / "manifest.json"), digest(raw)),
                                manifest["tree_sha256"], canonical(provenance).decode())
