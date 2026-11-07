import argparse
import sys
from pathlib import Path
from .adapters.arena import ArenaArtifactAdapter
from .dataset import render_dataset


def main():
    parser = argparse.ArgumentParser(prog="prism")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-arena", help="Verify ArtifactStore snapshots")
    importer.add_argument("--run-id", required=True)
    importer.add_argument("--artifact", type=Path, action="append", required=True,
                        help="explicit directory containing manifest.json and files/")
    viewer = commands.add_parser("serve", help="Open the local read-only run viewer")
    viewer.add_argument("--run-dir", type=Path, action="append", required=True,
                        help="Arena iterative run directory; repeat to compare runs")
    viewer.add_argument("--port", type=int, default=8765)
    viewer.add_argument("--open", action="store_true", help="Open the default browser")
    args = parser.parse_args()
    if args.command == "serve":
        from .viewer import serve
        if not 0 <= args.port <= 65535:
            parser.error("port must be between 0 and 65535")
        try:
            serve(args.run_dir, args.port, args.open)
        except (OSError, ValueError) as error:
            print(f"Viewer could not start: {error}", file=sys.stderr)
            return 1
        return 0
    if len(args.artifact) > 128:
        print("Import failed: at most 128 artifact directories per invocation.", file=sys.stderr)
        return 1
    try:
        adapter = ArenaArtifactAdapter(args.run_id)
        result = render_dataset([adapter.inspect(path) for path in args.artifact])
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print("Import failed: invalid, inaccessible or inconsistent artifact. No dataset emitted.", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
