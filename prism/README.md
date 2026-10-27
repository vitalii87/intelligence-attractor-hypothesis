# PRISM

**Version 0.1.0 — contract scaffold, not a finished analyzer.** PRISM is a working
name; name/package availability has not been checked. Distribution: `iah-prism`;
Python import: `prism`. Uses Python 3.11+, standard library only at runtime.

Independent offline measurement and comparison of versioned systems. Arena is a
future data source, not a runtime dependency. PRISM must be able to report
convergence, divergence, persistent differences and insufficient evidence equally.

## Present in this scaffold

- Entity/version, evidence reference, evaluation context and measurement records.
- Explicit measured / not-measured / incompatible / error statuses.
- Basic context compatibility checks, including environment identity for resources.
- Adapter and pair-metric extension protocols.
- Deterministic JSON report serialization and contract tests.

No actual Arena importer, behavioral/architectural metric, statistical inference,
CLI or visualization is implemented yet. Hash references are validated syntactically,
not checked against files. The compatibility helper is a prerequisite check, not
proof of a fair experimental comparison. Report records are an initial schema;
full provenance and experiment manifests remain work described in REQUIREMENTS.md.

## Layout

```text
prism/
  REQUIREMENTS.md          scientific and engineering acceptance requirements
  ROADMAP.md               implementation sequence
  pyproject.toml           standalone Python package
  src/prism/
    models.py              interchange records
    comparison.py          context checks
    adapters/              read-only import interface
    metrics/               versioned measurement interface
    reporting.py           JSON report serialization
  tests/                   contract checks
```

From `prism/` in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

See [requirements](REQUIREMENTS.md) and [roadmap](ROADMAP.md). The module follows
the repository's license; the scaffold does not alter publication or Arena versions.
