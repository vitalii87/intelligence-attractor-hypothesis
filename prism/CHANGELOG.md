# PRISM changelog

## 0.4.0 — 2026-11-07

- Add an independent read-only local viewer for Arena integer-sum iterative runs.
- Verify checkpoints, configuration, event chains and accepted artifacts; retain
  explicit unavailable/partial/error states and bounded, confined filesystem reads.
- Show quality and resource charts, attempts, event payloads, version comparisons,
  local researcher notes and JSON export without executing imported code.
- Add a Ukrainian interface with persistent section/run navigation, searchable
  lists, URL-restored filters, light/dark themes and a responsive mobile menu.
- Link the attempt side panel to its events and code, with adjacent-attempt
  navigation and a dedicated context/evidence section.
- Provide a PowerShell launcher, a loopback-only server and 16 additional tests.

The viewer reads saved observations; no paid model calls or automatic scientific
distance calculations are made. See [viewer usage and limits](VIEWER.md).

## 0.3.0 — 2026-10-31

- Add exact string-output disagreement over declared case/replicate keys.
- Refuse incompatible conditions; report missing and failed observations explicitly.
- Require complete successful coverage for a numeric score; retain partial diagnostics.
- Add deterministic JSON reports with contexts, observations, coverage and metric settings.
- Test known equal/divergent outputs, alignment, incompatibility and missing data.

Python API only: automatic Arena observation ingestion and a comparison CLI remain
unfinished. This metric does not measure quality, architecture or causal convergence.

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
