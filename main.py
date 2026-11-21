import sys

from cvss.cli import run


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "cli":
        run()
        return 0

    print("Usage: python main.py cli")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
