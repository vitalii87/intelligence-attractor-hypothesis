"""Bounded, read-only view of Arena's exploratory integer-sum iteration format.

No Arena imports, candidate execution, or inferred scientific measurements.
Checksums establish consistency, not authenticity. Read frozen runs for auditing;
live reads are best-effort and explicitly marked when the checkpoint changes.
"""
import difflib
import json
import os
from pathlib import Path
import re
import tomllib

from . import __version__
from .adapters.arena import ArenaArtifactAdapter, ImportFailure, _object, _read, _regular, canonical, digest

BUDGETS = ("model_calls", "input_tokens", "output_tokens", "cost_microusd",
           "compute_seconds", "edit_bytes", "edit_operations")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
HASH = re.compile(r"[a-f0-9]{64}\Z")
MAX_ATTEMPTS = 256


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ImportFailure("Nonfinite JSON")))


def budget(value):
    if not isinstance(value, dict):
        return {key: None for key in BUDGETS}
    return {key: value[key] if type(value.get(key)) is int and value[key] >= 0 else None
            for key in BUDGETS}


def score(value):
    if not isinstance(value, dict):
        return None
    fitness = value.get("fitness")
    number = fitness.get("correct_fraction") if isinstance(fitness, dict) else None
    return number if type(number) in (int, float) and 0 <= number <= 1 else None


class RunReader:
    def __init__(self, root):
        self.root = Path(os.path.abspath(root))
        for parent in reversed((self.root, *self.root.parents)):
            _regular(parent, directory=True)
        self.bytes_read = 0

    def path(self, name):
        if not isinstance(name, str) or any(c in name for c in ("\\", ":", "\0")):
            raise ImportFailure("Unsafe run path")
        parts = name.split("/")
        if any(p in ("", ".", "..") or p.endswith((".", " ")) for p in parts):
            raise ImportFailure("Unsafe run path")
        path = self.root
        for part in parts:
            path = path / part
            if path.exists() or path.is_symlink():
                _regular(path, directory=path.is_dir())
        return path

    def read(self, name, maximum=2_000_000):
        raw = _read(self.path(name), maximum)
        self.bytes_read += len(raw)
        if self.bytes_read > 64_000_000:
            raise ImportFailure("Run read limit exceeded (64 MB)")
        return raw

    def code(self, name, expected=None):
        raw = self.read(name, 256_000)
        sha = digest(raw)
        if expected is not None and sha != expected:
            raise ImportFailure("Candidate checksum mismatch")
        return {"path": name, "sha256": sha, "text": raw.decode("utf-8")}

    def events(self, name, lineage):
        raw = self.read(name, 4_000_000)
        pending = bool(raw and not raw.endswith(b"\n"))
        lines = raw.splitlines()
        if pending:
            lines = lines[:-1]  # Never treat an in-progress append as a complete event.
        if len(lines) > 2000:
            raise ImportFailure("Event limit exceeded (2000 per attempt)")
        previous, result = "0" * 64, []
        for line in lines:
            if not line.strip():
                continue
            record = parse_json(line)
            event = record["event"]
            if (record["previous_event_hash"] != previous or
                    record["event_hash"] != digest(canonical({"event": event, "previous_event_hash": previous})) or
                    event["lineage_id"] != lineage or event.get("schema_version") != 1):
                raise ImportFailure("Event chain mismatch")
            if not isinstance(event.get("payload"), dict):
                raise ImportFailure("Invalid event payload")
            previous = record["event_hash"]
            result.append({key: event.get(key) for key in
                           ("event_type", "timestamp_utc", "event_id", "payload")})
        return result, pending


def load_run(root):
    reader = RunReader(root)
    checkpoint = reader.read("iteration-state.json", 8_000_000)
    envelope = parse_json(checkpoint)
    if not isinstance(envelope.get("payload"), str) or digest(envelope["payload"].encode()) != envelope.get("sha256"):
        raise ImportFailure("Checkpoint checksum mismatch")
    state = parse_json(envelope["payload"])
    config_raw = reader.read("config.toml", 256_000)
    if digest(config_raw) != state.get("config_sha256"):
        raise ImportFailure("Frozen configuration checksum mismatch")
    config = tomllib.loads(config_raw.decode("utf-8"))
    if config.get("schema_version") != 1 or config.get("task", {}).get("id") != "integer-sum":
        raise ImportFailure("Only Arena integer-sum iteration schema 1 is supported")
    if state.get("status") not in ("paused", "running", "complete"):
        raise ImportFailure("Unknown run status")
    history = state.get("history")
    if not isinstance(history, list) or len(history) > MAX_ATTEMPTS:
        raise ImportFailure("Invalid history or more than 256 attempts")
    settings = config.get("lineages")
    if not isinstance(settings, list) or not 1 <= len(settings) <= 32:
        raise ImportFailure("Expected 1–32 lineages")
    identifiers = [item.get("id") for item in settings]
    if any(not isinstance(i, str) or not SAFE_ID.fullmatch(i) for i in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ImportFailure("Invalid lineage identities")
    if not isinstance(state.get("lineages"), dict) or set(state["lineages"]) != set(identifiers):
        raise ImportFailure("Checkpoint/config lineage mismatch")
    run_id = digest(str(reader.root).encode())[:20]
    warnings, lineages, versions, attempts = [], [], [], []
    incumbent_hashes = {}
    total_events = 0
    for item in settings:
        row = state["lineages"][item["id"]]
        lineages.append({"id": item["id"], "model": item["model"], "origin": item["origin"],
                         "generation": row.get("generation"), "stop_reason": row.get("stop_reason"),
                         "usage": budget(row.get("usage")), "limits": budget(config.get("total"))})
        try:
            code = reader.code(f"seeds/{item['id']}/solver.py")
            incumbent_hashes[item["id"]] = code["sha256"]
            versions.append({"id": f"{item['id']}:seed", "lineage": item["id"], "label": "Seed",
                             "attempt": 0, "integrity": "read", **code})
        except (OSError, ValueError):
            warnings.append(f"{item['id']}: seed unavailable or invalid")
    jobs, counts = set(), {i: 0 for i in identifiers}
    rows = list(history)
    if state.get("inflight") is not None:
        if not isinstance(state["inflight"], dict):
            raise ImportFailure("Invalid inflight record")
        rows.append({**state["inflight"], "status": "running"})
    for row in rows:
        lineage, job = row.get("lineage"), row.get("job")
        if lineage not in identifiers or not isinstance(job, str) or not re.fullmatch(r"attempt-\d{6}", job) or job in jobs:
            raise ImportFailure("Invalid or duplicate attempt identity")
        if type(row.get("attempt")) is not int or row["attempt"] != counts[lineage] + 1:
            raise ImportFailure("Nonsequential lineage attempt")
        if type(row.get("epoch")) is not int or row["epoch"] < 1:
            raise ImportFailure("Invalid epoch")
        counts[lineage] += 1
        jobs.add(job)
        status = row.get("status")
        if status not in ("accepted", "rejected", "failed", "interrupted", "running"):
            raise ImportFailure("Unknown attempt status")
        evaluation = row.get("evaluation") or {}
        if not isinstance(evaluation, dict):
            raise ImportFailure("Invalid evaluation")
        acceptance = evaluation.get("acceptance") or {}
        if not isinstance(acceptance, dict):
            raise ImportFailure("Invalid acceptance")
        entry = {"id": job, "lineage": lineage, "attempt": row["attempt"], "epoch": row["epoch"],
                 "status": status, "baseline": score(row.get("baseline")), "quality": score(evaluation),
                 "reason": row.get("error") or acceptance.get("reason") or ("Attempt in progress" if status == "running" else None),
                 "spent": budget(row.get("spent")), "events": [], "event_integrity": "unavailable",
                 "artifact_integrity": "not_measured", "diff": None,
                 "reservation": budget(config.get("attempt")) if status in ("running", "interrupted") else None,
                 "net_changed_files": row.get("net_changed_files"),
                 "evaluation": {k: evaluation.get(k) for k in
                                ("correct", "cases", "invalid_outputs", "duration_ms", "timed_out_cases", "execution_failures")}}
        base = f"{job}/state/lineages/{lineage}"
        try:
            events, pending = reader.events(f"{base}/events.jsonl", lineage)
            total_events += len(events)
            if total_events > 20_000:
                raise ImportFailure("Run event limit exceeded (20000)")
            entry["events"] = events
            entry["event_integrity"] = "partial" if pending else "verified"
        except FileNotFoundError:
            entry["event_integrity"] = "pending" if status == "running" else "unavailable"
        except (OSError, ValueError, KeyError, TypeError):
            entry["event_integrity"] = "error"
            warnings.append(f"{job}: event log failed verification or exceeded limits")
        try:
            before = reader.code(f"{base}/workspace/accepted/gen-0000/files/solver.py", incumbent_hashes.get(lineage))
            if status == "accepted":
                artifact_id = row.get("artifact_id")
                if not isinstance(artifact_id, str) or not HASH.fullmatch(artifact_id):
                    raise ImportFailure("Missing artifact ID")
                source = reader.path(f"{job}/artifacts/sha256/{artifact_id[:2]}/{artifact_id}")
                adapter = ArenaArtifactAdapter(run_id)
                adapter.max_total_bytes, adapter.max_file_bytes, adapter.max_entries = 2_000_000, 256_000, 256
                imported = adapter.inspect(source)
                provenance = parse_json(imported.provenance_json)
                if provenance.get("lineage_id") != lineage or imported.entity.version_id != artifact_id:
                    raise ImportFailure("Artifact lineage mismatch")
                # Tie the verified snapshot to the checkpoint, not a caller-selected path.
                if row.get("accepted_path") != f"{base}/workspace/accepted/gen-0001/files":
                    raise ImportFailure("Unexpected accepted path")
                if not isinstance(row.get("accepted_sha256"), str) or not HASH.fullmatch(row["accepted_sha256"]):
                    raise ImportFailure("Missing accepted content checksum")
                after = reader.code(f"{base}/workspace/accepted/gen-0001/files/solver.py", row.get("accepted_sha256"))
                artifact_code = reader.code(f"{job}/artifacts/sha256/{artifact_id[:2]}/{artifact_id}/files/solver.py")
                if artifact_code["sha256"] != after["sha256"]:
                    raise ImportFailure("Artifact/checkpoint content mismatch")
                entry["artifact_integrity"] = "verified"
                incumbent_hashes[lineage] = after["sha256"]
                label = f"Accepted · #{row['attempt']}"
            else:
                name = f"{base}/workspace/rejected/epoch-0001-attempt-0001/files/solver.py"
                if not reader.path(name).exists():
                    name = f"{base}/workspace/attempts/epoch-0001-attempt-0001/files/solver.py"
                after = reader.code(name)
                label = f"{status.capitalize()} · #{row['attempt']}"
            entry["diff"] = "".join(difflib.unified_diff(before["text"].splitlines(True), after["text"].splitlines(True),
                                                       fromfile="incumbent/solver.py", tofile="candidate/solver.py"))
            versions.append({"id": job, "lineage": lineage, "label": label, "attempt": row["attempt"],
                             "integrity": entry["artifact_integrity"], **after})
        except (OSError, ValueError, KeyError, TypeError):
            if status == "accepted":
                incumbent_hashes.pop(lineage, None)
                entry["artifact_integrity"] = "error"
                warnings.append(f"{job}: accepted artifact or code failed verification")
            else:
                warnings.append(f"{job}: candidate code unavailable; no diff inferred")
        attempts.append(entry)
    changed = reader.read("iteration-state.json", 8_000_000) != checkpoint
    if changed:
        warnings.append("Checkpoint changed during read. Refresh; use a paused snapshot for an audit.")
    return {"schema_version": "prism-run-view-v1", "prism_version": __version__, "id": run_id,
            "name": reader.root.name, "source": str(reader.root), "status": state["status"],
            "arena_version": state.get("version"), "task": config["task"]["id"],
            "runtime": {k: config.get("runtime", {}).get(k) for k in ("engine", "image", "cpus", "memory_mb")},
            "snapshot_sha256": digest(checkpoint), "config_sha256": state["config_sha256"],
            "snapshot_changed": changed, "lineages": lineages, "attempts": attempts, "versions": versions,
            "warnings": warnings, "limitations": [
                "Behavioral distance and architecture are not measured: aligned per-case observations are unavailable.",
                "Costs are configured-price ledger estimates; interrupted or running attempts can retain reservations.",
                "Compute seconds are charged wall time, not CPU time. Checksums do not authenticate the producer.",
                "Read-only live views are best-effort; event chains cannot detect removal of a valid trailing suffix."]}
