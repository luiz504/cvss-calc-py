import argparse
import sys
from pathlib import Path

from cvss.cli import run_interactive, run_vector

USAGE = "Usage: python main.py cli [--vector CVSS:3.1/AV:N/...]"
PROGRAM = "cvss"
DESCRIPTION = "Calculate CVSS v3.1 base scores. Without options it asks the metrics interactively."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION, allow_abbrev=False)
    parser.add_argument("-v", "--vector", metavar="VECTOR", help="score this CVSS:3.1 vector and exit")
    parser.add_argument("-c", "--chart", action="store_true", help="also write the SVG chart to the temp folder")
    parser.add_argument("-o", "--output", metavar="PATH", help="write the SVG chart to PATH (implies --chart)")

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
