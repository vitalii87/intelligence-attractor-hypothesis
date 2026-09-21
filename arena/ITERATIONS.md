# Iterative runs — Arena 0.3.0

This is the configurable **exploratory runner**. It supports repeated attempts,
budgets, stopping and checkpoint recovery. `integer-sum` supports `scripted-v1`
and an OpenAI adapter; see [OPENAI.md](OPENAI.md) for paid API configuration.
The default example makes no paid calls. This is not the
preregistered EXP-001 runner and does not open a final holdout.

## Configure and run

Requirements: Python 3.11+; for arbitrary candidate execution use a running Linux
Docker engine and a locally downloaded digest-pinned Python image. Trusted local
mode executes only the bundled fixtures, not arbitrary edited programs.

From `arena/` in PowerShell:

```powershell
$env:PYTHONPATH = "src"
Copy-Item iteration.example.toml my-iteration.toml
# Edit my-iteration.toml before starting.
python -m iah_arena --version
python -m iah_arena iterate --config my-iteration.toml --output-dir exports/my-run --steps 2
python -m iah_arena iteration-status --run-dir exports/my-run
python -m iah_arena resume-iterations --run-dir exports/my-run
```

Omit `--steps` for continuous execution to a stopping condition. `--steps N`
pauses after N additional attempts in this invocation, across all lineages.
On Linux/macOS use `export PYTHONPATH=src` and `python3`.

From a second terminal, request a cooperative pause:

```powershell
python -m iah_arena pause-iterations --run-dir exports/my-run
```

The active attempt finishes and checkpoints before pausing. Resume clears an old
pause request. Ctrl+C is an abrupt interruption: the unfinished attempt follows
the conservative recovery policy below. There is no API-call retry loop hidden
inside this command.

## Editable parameters

All example values are **demonstration defaults**, not experimentally justified
budgets. Unknown keys, invalid types, unknown models and tasks are rejected.

| Section | Controls |
| --- | --- |
| `run` | Maximum epochs, minimum attempts before plateau stopping, plateau patience, consecutive failure limit, tool calls per attempt |
| `total` | Per-lineage cumulative model calls, tokens, monetary usage, charged compute seconds, edited bytes and file-edit operations |
| `attempt` | Upper reservation for each corresponding budget in one attempt |
| `runtime` | Engine/image, CPU allocation, RAM, process count, per-case timeout, temporary storage, output size |
| `workspace` | Maximum bytes per file and total candidate workspace bytes |
| `information` | Prompt characters, visible history/metrics/files and workspace-size limits |
| `task` | Task ID, strict improvement threshold, development and selection examples |
| `lineages` | Any positive number of unique IDs, starting structures and implemented model IDs |

`model = "scripted-v1"` uses zero token and monetary budgets in the default example.
`openai/<model-id>` requires Docker, nonzero budgets and an `[openai]` table.
API keys are not a supported configuration field and must not be placed in files
or histories. The OpenAI adapter reads a named environment variable separately.

Each configured epoch gives every active lineage one opportunity; order rotates
between epochs. Seeds may share an origin but IDs must differ. One accepted
candidate becomes the starting program for that lineage's next attempt.
All attempts use their own workspace and the same frozen task settings. Each
provider sees only its own candidate, metrics and bounded history.

The arithmetic fixtures accept lists of at most 16 integers with absolute values
at most 10^30. They are public integration cases, not hidden benchmarks. This
runner has one fixed stage: automatic curriculum transitions are future work.

## Budget semantics

An attempt starts only when its **whole configured reservation** fits the
remaining per-lineage budget. Arena saves that reservation before any attempt
work. After a completed checkpoint, unused resources are returned. This may
leave unusable remainder below one full reservation; it never increases limits.

- Every successful file write counts its entire UTF-8 replacement payload and
  one operation, including repeated or identical writes. Deletion counts the
  removed byte size and one operation. Refused/failed mutations do not consume
  edit budget. Rejected candidate attempts retain their successful edit costs.
- Final differences are reported separately as `net_changed_files` and
  `net_replaced_bytes` (old + new sizes for a changed solver). These currently
  cover the fixture's `solver.py`, not an arbitrary multi-file diff.
- Compute accounting charges each runtime invocation at least one whole wall
  second, rounding up. Requested timeouts are limited by remaining allowance.
  Accounting is capped at that allowance; timeout cleanup overhead is outside
  this measure. This is **not measured CPU time**. Docker's CPU/RAM/PID limits
  constrain candidate execution separately. Baseline, public tests and selection
  evaluations all consume the compute allowance.
- Trusted local mode enforces fixture/input restrictions, timeouts and returned
  output size, but does not enforce Docker CPU/RAM/PID limits.

Acceptance requires correctness improvement strictly greater than
`task.minimum_improvement`. Rejected attempts increase the plateau counter.
Consecutive raised execution/provider errors trigger `failure_limit`; errors also
count as non-improvements. A later normally completed attempt resets consecutive
failures. Budget or failure limits can stop a lineage before `min_attempts`.

## Frozen settings and recovery

The run copies the exact configuration to `config.toml`, records its SHA-256,
Arena version and source digest. Editing the original input file does not affect
an existing run. Editing the saved copy or changing Arena source blocks resume.
Create a new directory to try new parameters. Existing run directories are never
overwritten. Use the original source checkout to resume an older run.

The authoritative state is `iteration-state.json`: a checksummed envelope written
via a temporary file and atomic replacement, with file contents flushed to disk.
A process lock prevents two runners from advancing the same run. This detects
accidental corruption; it is not a cryptographic signature or backup system.

Each attempt gets its own controller workspace, event journal and artifacts.
The outer checkpoint decides which accepted program is current for the next
iteration. Internal generation numbers restart within each attempt; cumulative
lineage generation and iteration are recorded in the outer state and provenance.

If a process dies before checkpointing:

1. The cursor and attempt reservation have already been persisted.
2. Resume records the in-flight attempt as `interrupted` and retains its full
   reservation, because exact usage after a crash cannot be established.
3. Its files and any artifacts remain available for inspection. They are not
   automatically promoted, even if evaluation completed just before the crash.
4. The last checkpointed program stays current; scheduling continues with the
   next opportunity. The interrupted attempt is never silently replayed.

This is attempt-boundary recovery, not continuation of an unfinished model call
or restoration of a running container. Do not resume while an old controller is
still alive. Docker timeout cleanup is supported; killing the host abruptly may
leave an orphan container that needs inspection before resuming.

## Outputs and expected demonstration

The example produces nine attempts: three improvements, then six equivalent
replacements rejected. Each lineage stops at plateau with one accepted generation.
There are four scripted provider turns per attempt. All lineages retain different
program structures; no autonomous discovery or convergence result is implied.

`summary.json` is a convenient display copy of the latest saved state;
`iteration-status` reads the authoritative checkpoint. `attempt-*/state/` contains
per-attempt hash-chained events and programs; `attempt-*/artifacts/` holds accepted
artifacts. The history retains scores, usage, net changes, failures and stop reasons.
The live view is console output; Jenkins and a live GUI are not yet connected.

Exit code 0 means a clean pause/completion, including normal candidate rejection.
Code 1 reports setup failure or a run history containing failed/interrupted
attempts; code 130 reports Ctrl+C. Resuming does not erase prior errors.

`iteration.example.toml` is distinct from the existing `run.example.toml`, which
freezes the scientific experiment manifest and holdout lifecycle. Integration of
this runner with that lifecycle and a scientifically useful task
remains necessary before confirmatory experiments.
