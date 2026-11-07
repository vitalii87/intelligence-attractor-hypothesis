import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prism.adapters.arena import ImportFailure, canonical, digest
from prism.run_view import BUDGETS, RunReader, load_run


def put(root, path, data):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def checkpoint(root, state):
    payload = json.dumps(state, sort_keys=True, allow_nan=False)
    put(root, "iteration-state.json", canonical({"payload": payload, "sha256": digest(payload.encode())}))


def fixture(root):
    limits = "\n".join(f"{key} = 100" for key in BUDGETS)
    config = ('schema_version = 1\n[task]\nid = "integer-sum"\n[runtime]\nengine = "trusted-local"\n'
              f'[total]\n{limits}\n[attempt]\n{limits}\n'
              '[[lineages]]\nid = "a"\nmodel = "scripted-v1"\norigin = "loop"\n').encode()
    put(root, "config.toml", config)
    seed, candidate = b'print(0)\n', b"raise RuntimeError('never execute imported code')\n"
    put(root, "seeds/a/solver.py", seed)
    base = "attempt-000001/state/lineages/a/workspace"
    put(root, base + "/accepted/gen-0000/files/solver.py", seed)
    put(root, base + "/accepted/gen-0001/files/solver.py", candidate)
    inventory = [{"path": "solver.py", "size_bytes": len(candidate), "sha256": digest(candidate)}]
    identity = {"schema_version": 1, "artifact_type": "candidate", "tree_sha256": digest(canonical(inventory)),
                "files": inventory, "provenance": {"lineage_id": "a"}}
    aid = digest(canonical(identity))
    artifact = f"attempt-000001/artifacts/sha256/{aid[:2]}/{aid}"
    put(root, artifact + "/files/solver.py", candidate)
    put(root, artifact + "/manifest.json", canonical({**identity, "artifact_id": aid, "created_utc": "2026-11-01"}))
    event = {"schema_version": 1, "lineage_id": "a", "event_type": "tool_called", "event_id": "event-1",
             "timestamp_utc": "2026-11-01T12:00:00Z", "payload": {"name": "read_file"}}
    body = {"event": event, "previous_event_hash": "0" * 64}
    put(root, "attempt-000001/state/lineages/a/events.jsonl", canonical({**body, "event_hash": digest(canonical(body))}) + b"\n")
    state = {"version": "0.5.0", "config_sha256": digest(config), "status": "paused", "inflight": None,
             "lineages": {"a": {"generation": 1, "usage": dict.fromkeys(BUDGETS, 0), "stop_reason": None}},
             "history": [{"lineage": "a", "job": "attempt-000001", "attempt": 1, "epoch": 1, "status": "accepted",
                          "artifact_id": aid, "accepted_path": base + "/accepted/gen-0001/files", "accepted_sha256": digest(candidate),
                          "baseline": {"fitness": {"correct_fraction": 0}}, "evaluation": {"fitness": {"correct_fraction": 1}},
                          "spent": dict.fromkeys(BUDGETS, 0)}]}
    checkpoint(root, state)
    return state, artifact


class RunViewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state, self.artifact = fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_verified_readonly_actual_zero_and_no_execution(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = load_run(self.root)
        attempt = result["attempts"][0]
        self.assertEqual((attempt["baseline"], attempt["quality"]), (0, 1))
        self.assertEqual(attempt["event_integrity"], "verified")
        self.assertEqual(attempt["artifact_integrity"], "verified")
        self.assertIn("+raise RuntimeError", attempt["diff"])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_checkpoint_and_config_tampering(self):
        path = self.root / "iteration-state.json"
        original = path.read_bytes()
        value = json.loads(original)
        value["payload"] += " "
        path.write_bytes(canonical(value))
        with self.assertRaisesRegex(ImportFailure, "Checkpoint"):
            load_run(self.root)
        path.write_bytes(original)
        with (self.root / "config.toml").open("ab") as stream:
            stream.write(b"\n# changed")
        with self.assertRaisesRegex(ImportFailure, "configuration"):
            load_run(self.root)

    def test_duplicate_and_nonfinite_json(self):
        for content in (b'{"payload":"a","payload":"b"}', b'{"payload":NaN}'):
            put(self.root, "iteration-state.json", content)
            with self.assertRaises(ValueError):
                load_run(self.root)

    def test_tampered_artifact_is_visible_but_not_verified(self):
        put(self.root, self.artifact + "/files/solver.py", b"tampered")
        result = load_run(self.root)
        self.assertEqual(result["attempts"][0]["artifact_integrity"], "error")
        self.assertIsNone(result["attempts"][0]["diff"])
        self.assertEqual(len(result["versions"]), 1)
        self.assertTrue(result["warnings"])

    def test_broken_event_chain_omits_untrusted_events(self):
        path = self.root / "attempt-000001/state/lineages/a/events.jsonl"
        path.write_bytes(path.read_bytes().replace(b"read_file", b"evil_file"))
        result = load_run(self.root)
        self.assertEqual(result["attempts"][0]["event_integrity"], "error")
        self.assertEqual(result["attempts"][0]["events"], [])

    def test_partial_append_preserves_verified_prefix(self):
        path = self.root / "attempt-000001/state/lineages/a/events.jsonl"
        with path.open("ab") as stream:
            stream.write(b'{"event":')
        result = load_run(self.root)
        self.assertEqual(result["attempts"][0]["event_integrity"], "partial")
        self.assertEqual(len(result["attempts"][0]["events"]), 1)

    def test_failed_and_interrupted_keep_unknown_usage_and_quality(self):
        for status in ("failed", "interrupted"):
            row = {"lineage": "a", "job": "attempt-000002", "attempt": 2, "epoch": 2, "status": status}
            self.state["history"] = [self.state["history"][0], row]
            checkpoint(self.root, self.state)
            result = load_run(self.root)["attempts"][1]
            self.assertIsNone(result["quality"])
            self.assertIsNone(result["spent"]["cost_microusd"])
            self.assertEqual(result["status"], status)
            self.assertEqual(result["reservation"] is not None, status == "interrupted")

    def test_running_attempt_not_confused_with_completed_history(self):
        self.state["status"] = "running"
        self.state["inflight"] = {"lineage": "a", "job": "attempt-000002", "attempt": 2, "epoch": 2}
        checkpoint(self.root, self.state)
        result = load_run(self.root)["attempts"][1]
        self.assertEqual(result["status"], "running")
        self.assertEqual(result["event_integrity"], "pending")
        self.assertEqual(result["reservation"]["cost_microusd"], 100)

    def test_rejected_candidate_not_replaced_by_incumbent(self):
        row = {"lineage": "a", "job": "attempt-000002", "attempt": 2, "epoch": 2, "status": "rejected"}
        self.state["history"].append(row)
        base = "attempt-000002/state/lineages/a/workspace"
        put(self.root, base + "/accepted/gen-0000/files/solver.py", b"raise RuntimeError('never execute imported code')\n")
        put(self.root, base + "/rejected/epoch-0001-attempt-0001/files/solver.py", b"print(2)\n")
        checkpoint(self.root, self.state)
        result = load_run(self.root)
        self.assertIn("+print(2)", result["attempts"][1]["diff"])
        self.assertEqual(result["versions"][-1]["text"], "print(2)\n")

    def test_attempt_identity_and_traversal(self):
        original = copy.deepcopy(self.state)
        for field, value in (("job", "../secret"), ("lineage", "../secret"), ("attempt", 4), ("epoch", True)):
            self.state = copy.deepcopy(original)
            self.state["history"][0][field] = value
            checkpoint(self.root, self.state)
            with self.assertRaises(ImportFailure):
                load_run(self.root)

    def test_confined_paths_and_size_limits(self):
        reader = RunReader(self.root)
        for name in ("../secret", "/secret", "C:/secret", "x\\secret", "x/./y", "x./y"):
            with self.assertRaises(ImportFailure):
                reader.path(name)
        with self.assertRaises(ImportFailure):
            reader.read("config.toml", 1)

    def test_live_checkpoint_change_is_explicit(self):
        original_read = RunReader.read
        count = 0
        def read(reader, name, maximum=2_000_000):
            nonlocal count
            raw = original_read(reader, name, maximum)
            if name == "iteration-state.json":
                count += 1
                if count == 2:
                    return raw + b" "
            return raw
        with patch.object(RunReader, "read", read):
            result = load_run(self.root)
        self.assertTrue(result["snapshot_changed"])

    def test_no_arena_dependency(self):
        import sys
        self.assertFalse(any(k == "iah_arena" or k.startswith("iah_arena.") for k in sys.modules))


if __name__ == "__main__":
    unittest.main()
