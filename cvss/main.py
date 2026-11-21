import sys

from cvss.cli import run

if len(sys.argv) == 2 and sys.argv[1] == "cli":
    run()

else:
    print("Usage: python main.py cli")
    sys.exit(2)
