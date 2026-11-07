# PRISM

**Version 0.4.0 — local experiment viewer and verified artifact import.** PRISM is a working
name; name/package availability has not been checked. Distribution: `iah-prism`;
Python import: `prism`. Uses Python 3.11+, standard library only at runtime.

Independent offline measurement and comparison of versioned systems. Arena ArtifactStore is a supported
data source, not a runtime dependency. PRISM must be able to report
convergence, divergence, persistent differences and insufficient evidence equally.

## Present in this scaffold

- Entity/version, evidence reference, evaluation context and measurement records.
- Explicit measured / not-measured / incompatible / error statuses.
- Basic context compatibility checks, including environment identity for resources.
- Adapter and pair-metric extension protocols.
- Deterministic JSON report serialization and contract tests.
- Read-only Arena ArtifactStore importer, evidence verification and dataset manifest.
- `python -m prism import-arena` CLI; see [import instructions](IMPORTING.md).
- Read-only local GUI with run/lineage navigation, quality and resource charts,
  searchable attempts/events, source comparisons and local review notes.
  Start with `./prism/Start-Prism.ps1` from the repository root;
  see [viewer instructions](VIEWER.md).

Exact output disagreement with explicit case/replicate alignment and coverage is
implemented as a Python API; see [behavior measurements](BEHAVIOR.md). Architectural
metrics and statistical inference are not implemented yet. The viewer displays saved
quality and resources; it does not calculate behavioral distance automatically.
The importer verifies evidence hashes, but record constructors
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
