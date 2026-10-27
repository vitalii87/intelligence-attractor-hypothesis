import json
from pathlib import Path
import tempfile
import unittest

from prism.adapters.arena import ArenaArtifactAdapter, ImportFailure, canonical, digest
from prism.dataset import dataset_manifest


def fixture(root):
    root.mkdir()
    (root / "files").mkdir()
    data = b"raise RuntimeError('must never execute imported code')\n"
    (root / "files" / "solver.py").write_bytes(data)
    files = [{"path": "solver.py", "size_bytes": len(data), "sha256": digest(data)}]
    identity = {"schema_version": 1, "artifact_type": "candidate", "tree_sha256": digest(canonical(files)),
                "files": files, "provenance": {"lineage_id": "a", "generation": 1, "parent_generation": 0}}
    manifest = {**identity, "artifact_id": digest(canonical(identity)), "created_utc": "2026-10-27T00:00:00Z"}
    (root / "manifest.json").write_bytes(canonical(manifest))
    return manifest


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "artifact"
        self.manifest = fixture(self.root)
        self.adapter = ArenaArtifactAdapter("run-1")

    def tearDown(self):
        self.tmp.cleanup()

    def test_readonly_import_and_repeatable_dataset(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        imported = self.adapter.inspect(self.root)
        self.assertEqual(imported.entity.version_id, self.manifest["artifact_id"])
        self.assertIsNone(imported.entity.parent_version_id)
        self.assertEqual(dataset_manifest([imported]), dataset_manifest([self.adapter.inspect(self.root)]))
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertNotEqual(imported.entity.entity_id, ArenaArtifactAdapter("run-2").inspect(self.root).entity.entity_id)

    def test_tampered_file_missing_and_unlisted(self):
        solver = self.root / "files" / "solver.py"
        solver.write_text("tampered")
        with self.assertRaises(ImportFailure):
            self.adapter.inspect(self.root)
        solver.unlink()
        with self.assertRaises(ImportFailure):
            self.adapter.inspect(self.root)

    def test_unlisted_file(self):
        (self.root / "files" / "extra").write_text("x")
        with self.assertRaisesRegex(ImportFailure, "unlisted"):
            self.adapter.inspect(self.root)

    def test_identity_and_duplicate_json_keys(self):
        path = self.root / "manifest.json"
        changed = {**self.manifest, "artifact_type": "changed"}
        path.write_bytes(canonical(changed))
        with self.assertRaisesRegex(ImportFailure, "identity"):
            self.adapter.inspect(self.root)
        path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(ImportFailure):
            self.adapter.inspect(self.root)

    def test_unsafe_paths_rejected_before_read(self):
        for name in ("../outside", "/absolute", "C:/secret", "dir\\file", "a//b", "a/./b"):
            manifest = json.loads(json.dumps(self.manifest))
            manifest["files"][0]["path"] = name
            (self.root / "manifest.json").write_bytes(canonical(manifest))
            with self.assertRaisesRegex(ImportFailure, "unsafe"):
                self.adapter.inspect(self.root)

    def test_size_and_entry_limits(self):
        self.adapter.max_file_bytes = 1
        with self.assertRaises(ImportFailure):
            self.adapter.inspect(self.root)

    def test_duplicate_dataset_version_rejected(self):
        imported = self.adapter.inspect(self.root)
        with self.assertRaises(ImportFailure):
            dataset_manifest([imported, imported])
