> Implementation update 0.2.0: Arena ArtifactStore snapshot import, evidence digest verification, parsing limits and dataset manifests are now implemented. Full observation/run alignment and scientific metrics remain planned. See IMPORTING.md.

# PRISM requirements

Status: design baseline, 2026-10-27. Version 0.1.0 implements only the contract
scaffold identified in README.md. Requirements below are targets unless explicitly
marked implemented. They are not a preregistration of an IAH experiment.

## 1. Purpose and scope

Analyze versioned agents, programs and other observable systems through explicit,
separate measurement levels. Accept offline artifacts from Arena and future external
sources. A universal interchange contract must not imply universally meaningful
metrics. Black-box systems expose behavior, not automatically architecture.

PRISM must not optimize candidates, modify source evidence, reward architectural
similarity, or claim that improved task quality alone supports IAH. No universal
similarity percentage is a default output. IAH-specific analyses are extensions,
not assumptions embedded in all measurements.

## 2. Object and observation contracts

- **R01 Identity:** distinguish entity, immutable version, parent version, lineage,
  replicate, origin intervention and experiment. Never treat successive iterations
  as independent replicates. Minimal entity/version scaffold is implemented.
- **R02 Evidence:** reference input artifacts by location and content digest;
  verify digests on import. Record adapter/schema version and transformations.
  Never execute imported code. Reference records exist; verification/import do not.
- **R03 Conditions:** record task, suite/case IDs, evaluator, protocol, environment,
  budgets and timestamps. Comparisons must expose missing/different conditions.
  Basic context checks are implemented; full experiment manifests are not.
- **R04 Missing data:** unknown, incompatible and failed measurements have no
  numerical value and a reason. A zero distance means measured equality under the
  metric, not missing access. Implemented in the basic measurement record.
- **R05 Access scope:** declare black-box, code-visible, traced or intervenable
  access. Do not infer unavailable internal properties as direct observations.

## 3. Metric contracts

- **R06 Reproducibility:** each metric declares ID, version, parameters, units,
  interpretation, required inputs, supported object types and known limitations.
  Preserve tool versions and randomness for stochastic computations.
- **R07 Independent levels:** report quality, behavior, strategy, algorithm,
  organization, resources and implementation separately. Composite metrics require
  explicit weights, normalization and visible component results.
- **R08 Pair alignment:** compare the same cases under a declared alignment rule.
  Missing cases cannot silently become agreement or be dropped. Report coverage.
- **R09 Invariance:** specify which transformations should preserve a metric:
  file renaming, code formatting, module renaming or equivalent output encodings.
  Test those invariances. Do not assume a distance is a mathematical metric unless
  its required properties have been established.
- **R10 Noisy measurements:** record repetitions and dispersion for time/memory;
  separate startup overhead, API latency and candidate execution where measurable.
  Matching environment IDs alone is insufficient to establish comparable timing.
- **R11 Interpretation:** model-generated algorithm labels or explanations must
  identify model, prompt, version and supporting evidence. Keep these outputs
  distinct from deterministic measurements and allow manual correction/audit.

Initial metric candidates: exact output disagreement on aligned cases; error
profiles; quality/regret supplied by a verified task evaluator; runtime/resource
profiles; file and dependency changes. Raw text/code similarity is secondary.
Graph extraction must state language support and unresolved dynamic dependencies.

## 4. Trajectories, origin and recursive improvement

- **R12 Trajectories:** compare fixed-budget and performance-matched views separately.
  Preserve failed runs, attrition and rejected attempts. Stage changes must not be
  mistaken for changes on a fixed anchor suite.
- **R13 Frontier:** identify proven optimum versus empirical best-observed score.
  Report assumptions for normalized regret. Optimal task output does not prove
  optimal system architecture.
- **R14 Origin:** distinguish association/predictability from causal attenuation.
  Causal claims require controlled origin interventions and an explicit analysis
  design. Report absolute effects separately from relative variance shares.
- **R15 Dependence:** pairwise distances sharing an entity are dependent; uncertainty
  procedures must respect lineage/replicate structure. Specify exclusions and
  sensitivity analyses before confirmatory results are inspected.
- **R16 Recursive improvement:** separate edits to the solver from edits to the
  improvement mechanism. Compare old/new mechanisms on matched subsequent tasks
  and budgets using trials run by Arena or another executor. Structural change
  alone is not evidence of improved capacity for further improvement.
- **R17 Degeneracy:** support multiple equally competitive solution families and
  cluster stability. Do not force one canonical architecture into scoring.

## 5. Architecture and operation

- **R18 Independence:** PRISM imports no Arena runtime or provider SDK. Adapter
  implementation belongs behind a boundary; analysis can run with networking off.
- **R19 Plugins:** adding a metric/adapter must not require rewriting core records.
  Discovery must not automatically execute arbitrary third-party packages.
- **R20 Resource bounds:** importers must limit file sizes, counts and parsing work;
  reject unsafe traversal/archive paths and links. Candidate artifacts are untrusted.
- **R21 Provenance:** a report must bind the exact dataset manifest, metric settings,
  source/software versions and evidence used. Cache entries must invalidate when
  any relevant input or setting changes. Checksums are not signatures.
- **R22 Outputs:** stable machine-readable JSON first, then tables/HTML/plots with
  units, coverage, uncertainty, limitations and links to evidence. Basic JSON
  serialization is implemented; a complete report bundle is not.
- **R23 Separation from feedback:** research-only metrics are not sent to agents by
  default. Any feedback metric must be explicitly declared in the experimental
  protocol to avoid selecting for apparent convergence.
- **R24 Privacy:** no credentials in reports; minimize/flag sensitive prompt content.
  No external model-assisted interpretation without explicit configuration.

## 6. Acceptance examples for a usable first release

1. Import two frozen Arena runs read-only and reject a deliberately altered artifact.
2. Compare aligned behavior and refuse an incompatible suite/protocol comparison.
3. Show `not_measured` for unavailable architecture data, never a zero distance.
4. Reproduce a report from its manifest and verify unchanged raw inputs.
5. Display equal quality with different behavior/structure without calling it failure.
6. Preserve failure and attrition counts in a multi-lineage trajectory report.
7. Demonstrate a known convergence fixture, divergence fixture and persistent-
   difference fixture without using their labels as inputs to the measurements.

Only basic contract tests exist today. A useful initial analyzer additionally needs
an importer, real measurements, provenance assembly and end-to-end fixtures.
