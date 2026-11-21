import sys

from cvss.cli import run, run_vector

USAGE = "Usage: python main.py cli [--vector CVSS:3.1/AV:N/...]"


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "cli":
        run()
        return 0

    if len(argv) == 4 and argv[1] == "cli" and argv[2] == "--vector":
        return run_vector(argv[3])

    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
