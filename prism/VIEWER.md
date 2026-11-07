# Local Prism viewer — 0.4.0

An independent, read-only browser interface for Arena's exploratory `iterate`
format (`integer-sum`, configuration schema 1). Python 3.11+, standard library only;
no Node install, cloud account, API key, Docker, or Arena Python import is needed.

## Start

From the repository root in PowerShell:

```powershell
./prism/Start-Prism.ps1
```

On this workstation this opens the existing single-agent readiness run. To choose
other runs, including future GPT runs:

```powershell
./prism/Start-Prism.ps1 -RunDir './arena/exports/gpt-smoke-001'
./prism/Start-Prism.ps1 -RunDir './arena/exports/run-a','./arena/exports/run-b' -Port 8765
```

The launcher uses the local Python311 installation if present, then Python from
PATH (excluding the WindowsApps alias). Override with `-Python 'C:/path/python.exe'`.
It opens the browser; use `-NoBrowser` to suppress that. Stop with Ctrl+C in the
launching terminal. If the port is already occupied, choose another `-Port`.

Portable CLI from `prism/` (set `PYTHONPATH=src`, or install the package):

```text
python -m prism serve --run-dir /absolute/path/to/run --port 8765 --open
```

Repeat `--run-dir` for up to 32 explicitly chosen directories. The server reads
only registered runs and serves on `http://127.0.0.1:8765`. It does not discover or
serve arbitrary filesystem paths. There is no launch/pause/stop control for Arena.

## Interface

- **Navigation:** persistent sidebar with run search and five sections, lineage
  selector, contextual titles, light/dark themes and a collapsible mobile menu.
  The selected section, run, lineage, filters, code comparison and open attempt
  are stored in the URL; reload and browser Back/Forward restore them. Bookmarks
  assume the same registered run-directory order when restarting the server.
- **Overview:** completion summary, accepted quality, attempts, ledger cost,
  input/output tokens, trajectory, budgets and recent attempts.
- **Attempts:** accepted/rejected/failed/interrupted/running; search, status
  filter and ordering. The side panel shows the evaluator reason, measurements,
  source diff and notes, with previous/next navigation across the selected lineage
  and direct links to that attempt's events and code.
- **Events:** verified hash-chain records, chronological ordering within each
  global attempt, text/attempt/category filters, expandable tool payloads, and
  progressive display. Expanded records remain open during refresh.
- **Code:** seed, accepted and rejected snapshots; select two versions to inspect
  their source side by side and see their changed block. This is an exact text
  comparison, not a minimal-edit or architectural similarity measurement.
- **Review:** per-attempt notes in browser localStorage; JSON export includes
  the displayed run and those notes with checkpoint hashes and timestamps.
- **Context and evidence:** model, environment, checkpoint, source directory,
  per-attempt integrity results and explicitly unavailable scientific measurements.
- **Refresh:** manual or optional five-second polling; no automatic paid calls.

Keyboard: `/` focuses search for the current section (or run search), `?` opens
navigation help, and Escape closes details/help/mobile navigation. The theme is
saved in this browser. UI settings do not modify run files.

Notes belong to the browser origin (host + port), run path identity and attempt.
Changing browser/port or clearing browser storage makes them unavailable there.
Export JSON before moving environments. Notes never modify the source run.
Exports contain code, tool payloads and local paths: review them before sharing.

## Integrity and interpretation

The reader verifies the checkpoint envelope, frozen config hash, event chains,
accepted ArtifactStore contents and their correspondence to accepted code. Before
code is checked against the preceding known incumbent when available. Unavailable
or invalid artifact evidence produces a visible warning, not a verified badge.
Seed/rejected text is read and hashed; it is not a verified ArtifactStore version.
Global attempt IDs come from the iteration checkpoint, not local per-attempt
epoch/generation counters. Successive attempts are not independent replicates.

This is a viewing adapter, not a complete scientific run interchange format.
Quality is the saved `correct_fraction`; there is no re-evaluation. Behavioral
distance and architecture stay **not measured** without aligned case observations.
Ledger costs are estimates at configured prices and may include retained
reservations. A running/interrupted attempt has unknown actual spend, not zero.
Compute seconds are charged wall time, not measured CPU time. Timing includes
runtime overhead and must not be treated as a controlled performance experiment.

Live reads are best-effort. Partial JSONL tails are omitted and marked partial;
a checkpoint change during reading is reported. Freeze/pause a run for auditing.
Hashes do not authenticate the author, and chains cannot detect removal of a valid
trailing suffix. This is not a sandbox against a concurrent filesystem attacker.

Limits: 32 lineages/run, 256 completed attempts, 8 MB checkpoint, 256 KB code file,
2,000 events/attempt, 20,000 displayed events/run, 64 MB reader budget; existing
ArtifactStore verification also applies with tighter per-artifact bounds.
Links/reparse points and unsafe paths are refused. Imported code is never executed.
The server checks Host/Origin, emits CSP and no-store headers, has no mutation API,
and loads no third-party scripts, fonts or analytics.

## Verification

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

HTTP tests require permission for a temporary loopback socket. Reader tests cover
tampered states/config/artifacts/events, incomplete appends, missing measurements,
rejected candidates, retained reservations, path confinement and read-only import.
Browser verification uses the real single-agent run plus the older multi-lineage run.
The navigation refresh was checked at desktop and 390px mobile widths, including
filtered reload, browser Back, detail-to-events/code transitions, version swapping,
theme persistence, switching runs/lineages and the empty-attempt state.
