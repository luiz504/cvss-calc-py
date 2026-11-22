import argparse
import sys

from cvss.cli import run_interactive, run_vector

USAGE = "Usage: python main.py cli [--vector CVSS:3.1/AV:N/...]"
PROGRAM = "cvss"
DESCRIPTION = "Calculate CVSS v3.1 base scores. Without options it asks the metrics interactively."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION, allow_abbrev=False)
    parser.add_argument("-v", "--vector", metavar="VECTOR", help="score this CVSS:3.1 vector and exit")
    parser.add_argument("-c", "--chart", action="store_true", help="also write the SVG chart to the temp folder")

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()

    args = parser.parse_args(argv)
    if args.vector is not None:
        return run_vector(args.vector)

    run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
