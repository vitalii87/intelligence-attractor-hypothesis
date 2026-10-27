import argparse
import sys
from pathlib import Path
from .adapters.arena import ArenaArtifactAdapter
from .dataset import render_dataset


def main():
    parser = argparse.ArgumentParser(prog="prism")
    parser.add_argument("command", choices=["import-arena"])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--artifact", type=Path, action="append", required=True,
                        help="explicit directory containing manifest.json and files/")
    args = parser.parse_args()
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
