import sys

from cvss.cli import run
from cvss.web import serve


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "cli":
        run()
        return 0

    if len(argv) == 2 and argv[1] == "web":
        serve()
        return 0

    print("Usage: python main.py cli|web")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
