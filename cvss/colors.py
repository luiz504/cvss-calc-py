import os

RESET = "\033[0m"

STYLES = {
    "bold": "1",
    "dim": "2",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "critical": "1;97;41",
}


def enabled() -> bool:
    # Colors are always on, even into a pipe, to keep the output easy to read. Two standard opt-outs still apply:
    # a non-empty NO_COLOR (https://no-color.org) and a dumb terminal that cannot show colors.
    if os.environ.get("NO_COLOR"):
        return False

    return os.environ.get("TERM") != "dumb"


def paint(text: str, style: str) -> str:
    if not enabled():
        return text

    return f"\033[{STYLES[style]}m{text}{RESET}"
