# IAH Arena

IAH Arena is a task-independent laboratory for improving candidate programs in separate software lineages. A task plug-in supplies the problem, interface and evaluator; Arena supplies editing tools, execution boundaries, acceptance rules and records. Games, numerical problems and other measurable tasks can use this boundary, but each needs an implemented plug-in.

**Status:** core infrastructure plus a runnable `integer-sum` integration demo. Three scripted providers apply predetermined fixes to three distinct Python implementations. No external model provider is connected yet; no autonomous discovery or empirical support for IAH is claimed. A Docker execution path exists; the trusted local fixture mode also works without Docker.

## Start here

Requirements: Python **3.11 or newer**, a writable output directory and the standard library. From `arena/`:

```powershell
$env:PYTHONPATH = "src"
python -m iah_arena task-demo --task integer-sum --trusted-local --output-dir exports/sum-demo-001
```

On Linux/macOS use `PYTHONPATH=src python3 -m iah_arena task-demo --task integer-sum --trusted-local --output-dir exports/sum-demo-001`.

Watch per-lineage console messages and open `exports/sum-demo-001/report.html` afterwards. No API key or paid model call is needed. Use a new output directory for each run; existing runs are never overwritten. See [the demo guide](TASK_DEMO.md) for expected scores, Docker requirements, outputs and limits.

## What each component does

The evolving object is the candidate solution: code, algorithm and internal structure. The controller, editor, evaluator and resource policy remain fixed during a run. The agent chooses edits; the editor applies them mechanically without supplying a common refactoring strategy.

| Component | Responsibility |
| --- | --- |
| Task plug-in | Objective, input/output contract, suites, public tests and raw measurements |
| Provider adapter | Translate model calls into the same Arena tool contract |
| Workspace and tools | Apply edits, check hashes, separate attempts from accepted versions |
| Runtime | Run candidates under declared constraints; Docker for arbitrary candidate code |
| Fitness policy | Decide acceptance relative to the incumbent from measured results |
| Coordinator | Schedule independent lineages; three is an example, not a core limit |
| Events and artifacts | Preserve actions, failures, measurements and program provenance |
| Observer / Jenkins | Display progress and archive results; does not decide outcomes |

Each provider receives its own workspace, history and permitted feedback. Cross-lineage data belongs to the observer. In trusted local mode this is logical separation, not OS-level sandboxing.

## Extension and research expectations

Implement [`TaskPlugin`](src/iah_arena/tasking.py) to add a task: stable identities, curriculum, objective, public tests and a raw evaluator using an injected runtime. Supply seeds, an execution interface and a frozen fitness policy. See [`integer_sum.py`](src/iah_arena/tasks/integer_sum.py). Its demo interface is Python-only; language migration and games need appropriate task launch/build contracts. The current CLI exposes only `integer-sum`; this is an extension boundary, not automatic support for every problem.

For IAH, good task scores are insufficient. A scientific run also needs all suite layers, controlled holdout access, repeated origins/seeds, a frontier estimate and prespecified diversity/origin-dependence measurements. Persistent different high-performing solutions are a valid outcome. The demonstration task does not replace the EXP-001 design or preregistration.

No Jenkins service or live GUI is included yet. Jenkins can wrap the CLI, show its console output and archive reports; HTML Publisher can present `report.html`. Cooperative pause/resume and Jenkins integration remain future work. A CI retry must not silently restart an interrupted scientific run.

## Design boundary

The arena is trusted infrastructure. Its design boundary includes:

- provider-neutral decision sessions;
- prompt and tool schemas;
- transactional candidate workspaces;
- build and public-test execution;
- isolated judge execution;
- curriculum scheduling;
- budgets and stopping rules;
- immutable telemetry and artifact provenance;
- deterministic acceptance and rejection.

Candidate programs are untrusted and may modify only their assigned workspace. They must never receive provider credentials, evaluator source, hidden instances, neighboring lineage state, Docker control, or arena internals.

## Two clocks

The architecture distinguishes:

- **decision epochs**, in which an external model inspects evidence and proposes changes;
- **local compute phases**, in which builds, tests, profiling, and bounded searches run without model tokens.

This permits infrequent model calls while preserving autonomous local experimentation.

## Current foundation

The Python package now provides:

- domain identifiers and event types;
- an append-only JSONL event store with a SHA-256 hash chain;
- hard API and local-compute budgets;
- a canonical provider adapter protocol;
- an explicit upgrade-attempt lifecycle;
- copy-on-attempt workspaces with promotion and rollback-by-rejection;
- canonical, path-confined file/test/submit tools;
- atomic single-file writes that preserve existing content on write or replacement failure;
- mandatory SHA-256 preconditions for file edits and deletion, rejecting stale proposals;
- a bounded provider tool loop and deterministic fake provider;
- end-to-end candidate submission and evaluator-controlled acceptance;
- a Docker runtime boundary for isolated workshop and read-only judge commands;
- a common polyglot image recipe that permits language migration;
- frozen task/curriculum contracts and explicit benchmark layers;
- component-preserving Pareto or weighted fitness acceptance;
- content-and-provenance-addressed accepted-candidate artifacts;
- a frozen experiment-run state machine with a one-shot final-holdout gate;
- validated cross-lineage event and long-form metric exports;
- strict TOML run configuration and CLI lifecycle control;
- deterministic information-budgeted prompts with structured improvement claims;
- a sequential rotating coordinator for independent lineage turns;
- a CLI for creating a lineage, verifying telemetry, and running a free local dry run;
- dependency-free unit tests.

No task-specific score, preferred language, or provider SDK is embedded in this layer.

File mutation tools require `expected_sha256`: pass the exact-byte digest returned by
`read_file` or a successful write. For `write_file`, `null` means the path must not
exist. Missing or mismatched digests are rejected without applying the edit; read
the file again before retrying. Reads preserve UTF-8 content including CRLF line
endings. This changes the tool contract for callers that previously omitted the
digest. The check assumes sequential access to each workspace; it is not a lock
against concurrent external writers or running candidate processes.

The container recipe and operational notes are in [`docker/README.md`](docker/README.md). Docker image tags are rejected at runtime: the experiment must use a registry digest or local SHA-256 image ID.

The world-independent task boundary, curriculum rules, fitness policy, and artifact requirements are documented in [`TASK_PLUGINS.md`](TASK_PLUGINS.md).

Run freezing, holdout access control, and analysis exports are documented in [`EXPERIMENT_RUNS.md`](EXPERIMENT_RUNS.md).

Configuration, prompt fairness, crash recovery, and lineage scheduling are documented in [`OPTIMIZATION_CONTROL.md`](OPTIMIZATION_CONTROL.md).

## Planned architecture

```text
Trusted host
├── Arena controller
│   ├── provider adapters
│   ├── canonical tool loop
│   ├── budget ledger
│   ├── curriculum scheduler
│   └── event and artifact stores
├── Workshop A ── mutable candidate workspace
├── Workshop B ── mutable candidate workspace
├── Workshop C ── mutable candidate workspace
└── Judge ─────── fresh immutable evaluation container
```

The three workshops will share the same pinned polyglot image while using separate workspaces. Judge evaluations should run sequentially on the same host to reduce hardware contention.

## Event integrity

Each event record contains:

- a schema version;
- lineage, epoch, generation, and attempt identifiers;
- an event type and JSON payload;
- the hash of the previous event;
- a hash of the complete new record.

The chain detects accidental editing, truncation in the middle of a record, reordering, and cross-lineage mixing. It is provenance protection, not a substitute for external backups or cryptographic signatures.

## Development

The package currently uses only the Python standard library.

From `arena/`:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m iah_arena init-lineage --state-dir state --lineage-id demo-001 --origin local-dry-run
python -m iah_arena verify-events --state-dir state --lineage-id demo-001
python -m iah_arena dry-run --state-dir state --lineage-id dry-run-001
python -m iah_arena docker-check --image "sha256:<local-image-id>"
python -m iah_arena export-telemetry --state-dir state --output-dir exports/pilot --lineage-id lineage-a --lineage-id lineage-b
```

Generated state and artifacts are ignored by Git.

## Near-term milestones

1. Validate the task demo in the pinned Docker image on the experiment host; a live container smoke test is still required.
2. Add cumulative action-budget accounting and connect all execution paths to compute accounting.
3. Persist coordinator state and connect it to curriculum transitions and interruption recovery.
4. Connect a real provider adapter and run an explicitly exploratory pilot.
5. Implement an informative EXP-001 task with all suite layers, freeze metrics and preregister before confirmatory runs.
6. Add Jenkins launch/report integration and expand observation as real runs require.
