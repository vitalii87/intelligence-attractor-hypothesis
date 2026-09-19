# Docker integration check — 2026-09-19

Scope: `integer-sum` demo, three scripted providers with distinct Python programs.
This validates execution plumbing; it is not empirical evidence for IAH, a timing
benchmark, or an adversarial sandbox audit.

Environment: Windows host, Docker Desktop Linux backend, Docker Engine **29.8.0**,
Linux/amd64 image:

```text
python@sha256:da047cb8f9d1d98e5c070f5300ba9f7274e33b8fc0e5be5ed88740aed1b95ba9
```

The image was obtained from `python:3.11-slim`, then all evaluations used the
immutable digest above. No test used the mutable tag as its runtime identifier.
The polyglot image recipe was not built in this check.

## Reproduce

With a running Linux Docker engine, download the pinned image once:

```powershell
docker pull python@sha256:da047cb8f9d1d98e5c070f5300ba9f7274e33b8fc0e5be5ed88740aed1b95ba9
```

From `arena/`, choose a new output directory:

```powershell
$env:PYTHONPATH = "src"
python -m iah_arena task-demo --task integer-sum --image python@sha256:da047cb8f9d1d98e5c070f5300ba9f7274e33b8fc0e5be5ed88740aed1b95ba9 --output-dir exports/sum-docker-check
```

Docker startup is included in the five-second case timeout. Run only after the
engine is ready. Do not interpret duration as algorithm performance.

## Observations

The first run (`sum-docker-20260919`) accepted all three replacements at 6/6,
but the first lineage's baseline was unexpectedly 0/6. The other baselines were
2/6. The baseline diagnostics retained at that point were insufficient to identify
the cause. Startup effects are a possibility, not an established explanation.
This run was kept; no scores were edited or overwritten.

The report was extended to retain complete baseline/candidate measurements and
counts of timeouts, execution failures and truncated outputs. A new run
(`sum-docker-20260919-repeat`) then produced:

| Structure | Baseline | Candidate | Accepted | Generation |
| --- | --- | --- | --- | --- |
| Loop | 2/6 | 6/6 | Yes | 1 |
| Recursive | 2/6 | 6/6 | Yes | 1 |
| Reduce | 2/6 | 6/6 | Yes | 1 |

All reported baseline/candidate execution-failure, timeout, invalid-output and
truncation counts in the repeat were zero. Public tests passed for each candidate.
The run used 45 case executions: six baseline, three public and six selection
cases per lineage. It retained 27 hash-chained events per lineage and three
distinct accepted artifacts. Programs retained their different structures.

The compact [machine-readable record](docker-smoke-20260919.json) includes both
runs and their source digests. Full local journals, programs and HTML reports
remain under the corresponding ignored `arena/exports/` directories. Source
digests differ because diagnostic reporting changed between runs.

The commands exercised Arena's existing no-network, read-only workspace,
non-root execution and resource-limit flags. This successful smoke test does not
establish resistance to hostile candidate code or prove cross-platform behavior.
