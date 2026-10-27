# PRISM

**Version 0.2.0 — verified artifact import and contract scaffold.** PRISM is a working
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
- Read-only Arena ArtifactStore importer, evidence verification and dataset manifest.
- `python -m prism import-arena` CLI; see [import instructions](IMPORTING.md).

No behavioral/architectural metric, statistical inference or visualization is
implemented yet. The importer verifies evidence hashes, but record constructors
alone only validate hash syntax. The compatibility helper is a prerequisite check,
not proof of a fair experimental comparison. Full run/observation import and
experiment manifests remain work described in REQUIREMENTS.md.

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
