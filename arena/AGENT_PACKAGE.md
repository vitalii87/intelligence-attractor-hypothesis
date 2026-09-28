# Mutable agent package prototype — 0.4.1

This is the first package-contract layer, not a completed recursive optimizer.
The existing `iterate` command is unchanged. No model gateway, cumulative token
cap, iteration-rate scheduler or automatic package promotion is connected yet.

A working copy contains `agent.json` with exactly:

```json
{"schema_version":1,"argv":["python3","-I","-B","agent.py"]}
```

The launcher reads this manifest afresh on every call. All package files,
including the manifest, may be changed by the running package. The manifest
selects an argv within the container; it cannot configure host mounts, environment
credentials, network or runtime limits. No host execution fallback is provided.

The controller appends `/arena-context/context.json` as the final argument.
This separately mounted read-only file contains the author's task text, a neutral
instruction, workspace inventory, entry contract, runtime limits and currently
available capabilities. It offers no planner/critic roles or suggested architecture.
Model access is explicitly unavailable in this prototype. The passport is rebuilt
for each launch, not accepted from candidate-authored configuration.

Use `run_package(working_copy, docker_runtime, limits, task_text)` from Python.
Only pass a disposable isolated working copy, never an accepted artifact or the
repository. Files persist in that copy across launches; container temporary files
do not. The returned record includes before/after hashes and runtime results.
An invalid manifest after execution marks `package_valid=false`; structural
validity is not evidence of task quality or architectural improvement.

Pre/post checks reject links and bound the package to 256 files, 256000 bytes per
file and 2000000 bytes overall. These are prototype validation limits, **not a live
disk quota**. Do not expose this writable launcher to autonomous paid runs until
live write/resource accounting, rollback and promotion have been integrated.
Runtime adapters are trusted controller code; use DockerRuntime for candidate code.

Validation on 2026-09-28: simulated runtime tests cover entry reload, persistent
files, external read-only context and invalid self-edits. A real Docker smoke
attempt was blocked because the local Linux Docker engine was not running;
actual container execution of this prototype remains unverified.

Next: connect the package to disposable attempt snapshots and bounded model-call
requests. Then enforce input/output/combined tokens per iteration and a durable
iteration-rate limit. Only after that should this replace the current externally
directed editing loop. The API model's weights remain outside the mutable package.
