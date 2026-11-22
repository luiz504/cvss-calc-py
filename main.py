import argparse
import os
import sys
from pathlib import Path

from cvss.cli import run_interactive, run_vector

PROGRAM = "cvss"
DESCRIPTION = "Calculate CVSS v3.1 base scores. Without options it asks the metrics interactively."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION, allow_abbrev=False)
    parser.add_argument("-v", "--vector", metavar="VECTOR", help="score this CVSS:3.1 vector and exit")
    parser.add_argument(
        "-c", "--chart", action="store_true", help="also write the SVG chart to the temp folder and print its path"
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="write the SVG chart to FILE (a file, not a folder; overwritten if it exists; implies --chart)",
    )

    return parser


def find_output_problem(output: str) -> str | None:
    path = Path(output)
    folder = path.parent

    if path.is_dir():
        return f"{output} is a directory"

    if not folder.exists():
        return f"directory {folder} does not exist"

    if not folder.is_dir():
        return f"{folder} is not a directory"

    if not os.access(folder, os.W_OK | os.X_OK):
        return f"permission denied: cannot write in {folder}"

    if path.exists() and not os.access(path, os.W_OK):
        return f"permission denied: cannot overwrite {output}"

    return None


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output is not None:
        problem = find_output_problem(args.output)
        if problem is not None:
            parser.error(problem)

    if args.vector is not None:
        return run_vector(args.vector)

    run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
