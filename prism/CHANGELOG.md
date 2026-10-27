# PRISM changelog

## 0.2.0 — 2026-10-27

- Add bounded read-only Arena ArtifactStore v1 verification without an Arena dependency.
- Verify content/provenance identity, file-tree hash and each file's size/digest.
- Reject traversal, links, unlisted/missing files and ambiguous JSON/path records.
- Add run-scoped entity identities, deterministic dataset manifests and import CLI.
- Validate with 11 unit tests and a real Arena ArtifactStore smoke import.

Whole-run observations, suite alignment and scientific metrics remain unfinished.

## 0.1.0 — 2026-10-27

- Create an independent Python package scaffold without an Arena dependency.
- Define entity versions, evidence references, contexts and explicit result states.
- Add basic compatibility checks and JSON report serialization.
- Define adapter and pair-metric protocols, requirements and implementation roadmap.

No concrete scientific metrics or Arena importer implemented in this version.
