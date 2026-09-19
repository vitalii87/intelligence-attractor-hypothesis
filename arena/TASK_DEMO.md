# First task: integer sum

This is an engineering integration demonstration, not an IAH experiment.

## Task and expected behavior

The candidate accepts one JSON list of signed integers as its first command-line
argument and writes exactly one JSON integer to stdout: their sum. Empty lists
sum to zero. Three bundled Python structures are used: a loop, recursion and
reduction. All seeds deliberately discard negative inputs; their scripted fixes
remove this defect while retaining different structures.

Each lineage gets one four-turn attempt: read, edit with SHA-256 precondition,
public tests, submit. All use the same tool contract and strict correctness
improvement policy. Expected selection scores are **2/6 before** and **6/6 after**,
with three accepted generation-1 programs. Duration is diagnostic, not fitness.
The replacements are predetermined, not independently discovered by AI.

Development and selection fixtures are public in source. Anchor, regression and
final-holdout identities are reserved but not implemented or opened here. This
demo does not exercise the preregistered run lifecycle or measure convergence.

## Requirements and local run

Python 3.11+, standard library, writable output directory; no keys or model fees.
From `arena/` in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m iah_arena task-demo --task integer-sum --trusted-local --output-dir exports/sum-demo-001
```

On Linux/macOS prefix the command with `PYTHONPATH=src` and use `python3`.
Use your installed interpreter's full path if `python` is not on PATH.

The terminal shows baseline scores and each acceptance result. Open
`exports/sum-demo-001/report.html` in a browser. This is a static report, not a live
GUI. Existing output directories are refused, so choose a fresh name per run.
Exit code 0 means all scripted fixes were accepted. Rejected or failed attempts
produce a nonzero exit status and a report when possible; failures in one lineage
do not prevent others from receiving their turn.

Trusted local mode accepts only exact bundled source fixtures and bounded inputs.
Modified/unrecognized programs are refused. Verified source executes directly in
an empty temporary directory; candidate imports cannot load workspace helpers.
This is not a sandbox, does not enforce Docker CPU/RAM isolation and must not be
extended to arbitrary model-generated code. Cumulative local compute and edited
byte/file budgets are not yet charged by this demo.

## Docker mode

Requirements: a running Linux-container Docker engine and a pinned image with
`python3`. On Windows, start Docker Desktop. The intended common environment is
the [polyglot image](docker/README.md).

```powershell
python -m iah_arena task-demo --task integer-sum --image "sha256:<local-image-id>" --output-dir exports/sum-docker-001
```

The controller stays on the trusted host. Each case runs in a fresh container
with a read-only candidate workspace, no network and no other lineage mount.
Limits are one CPU allocation, 128 MiB memory, 32 processes and five seconds per
case. This still uses scripted providers. It is not Docker-in-Docker; candidates
never receive Docker control, evaluator source or provider credentials.

Before creating a run, the CLI checks that the engine uses Linux containers and
the pinned image is already present locally. Each check has a ten-second timeout.
It does not pull an image automatically. Failed prerequisites produce a readable
error and no experiment directory. This check does not verify Python availability
or mounting: a successful live smoke run is still required.

Docker exit codes 125/126/127 are treated conservatively as launch/infrastructure
errors, not zero-fitness candidates. Normal candidate failures remain evaluation
results. An explicit candidate exit with a reserved code will also be classified
as an infrastructure error. See [Docker exit status](https://docs.docker.com/engine/containers/run/#exit-status).

Live Docker execution passed on **2026-09-19**, using Docker Engine 29.8.0 and
the Linux/amd64 Python image pinned in the [verification record](validation/DOCKER_SMOKE.md).
All three lineages improved from 2/6 to 6/6 on the repeat, with zero baseline or
candidate execution failures, timeouts or truncated outputs. The first run's
anomalous initial score is preserved and discussed in that record. The full
polyglot image remains unverified; this check covers the arithmetic task only.

## Outputs

| Path inside the output directory | Purpose |
| --- | --- |
| `manifest.json` | Task/evaluator identities, curriculum hash, environment label, source hashes and origins |
| `summary.json`, `report.html` | Before/after scores, complete baseline/candidate evaluations, timeout/failure counts and interpretation |
| `state/lineages/` | Separate event journals and original/accepted/rejected program versions |
| `artifacts/` | Accepted programs addressed by content and provenance |
| `telemetry/` | Validated events, numeric metrics CSV and export manifest |

The manifest records source hashes, including uncommitted edits, rather than
pretending a Git commit identifies the current source tree exactly. It does not
capture the entire host environment. Timings and event timestamps will vary.

## Next steps

Validate the full polyglot image, finish budget enforcement and recovery, then connect a
real provider for an exploratory pilot. A useful scientific task must offer
measurable constraints and meaningful alternative solutions, with metrics fixed
before outcomes are inspected. A separate game or numerical task belongs in a
new plug-in; Arena's acceptance and editing machinery should stay task-neutral.
