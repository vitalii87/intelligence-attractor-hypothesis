# Arena changelog

## 0.2.0 — 2026-09-19

- Add strict editable `iteration.example.toml` settings for iterative exploration.
- Persist rotating lineage scheduling, accepted candidates, usage and stop reasons.
- Add start, status, cooperative pause and resume CLI commands.
- Freeze configuration, Arena version and source digest per run.
- Reserve budgets before attempts; preserve reservations after interrupted work.
- Enforce per-attempt edit budgets and cumulative reservation limits.
- Meter baseline, public-test and selection runtime calls separately from Docker CPU/RAM limits.
- Preserve complete attempted work and use the last checkpointed candidate on recovery.
- Add checks for pause/resume, crashes around promotion, corrupted state, changed settings,
  budget exhaustion, stopping, locks and rejected edits.

Only the arithmetic task and scripted providers are connected. This release is
infrastructure development, not a revision of the IAH v0.1 publication.

Validation: 92 unit tests run (91 passed, one optional Docker test skipped).
Separate real local and Docker CLI runs paused after two attempts and resumed
to nine attempts: three accepted, six rejected, all three lineages stopped at
plateau. Docker used the pinned Python image recorded in `validation/DOCKER_SMOKE.md`.
The first Docker baseline had one case timeout (1/6 correct rather than the
expected 2/6); subsequent baselines and all accepted candidates behaved as
expected. This smoke run verifies orchestration, not timing-stable scientific
measurement; startup/load sensitivity still needs treatment before experiments.

## 0.1.0

Initial Arena foundation; atomic edits, SHA-256 preconditions, arithmetic demo,
Docker prerequisite checks and live Docker verification added during development.
