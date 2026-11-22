#!/bin/sh
# cvss installer: ONE self-contained file made by ./build.sh. The project's wheel is appended after the marker line at
# the bottom, so installing needs no source folder, no make and no network (only Python 3.12+ with the venv module).
#
#   sh cvss-<version>-installer.sh              install or upgrade for the current user (no sudo)
#   sh cvss-<version>-installer.sh --uninstall  remove everything it installed
#
# It creates a private virtual environment in ~/.local/share/cvss, installs the wheel into it, then links the command
# into ~/.local/bin and the man page into ~/.local/share/man.

set -eu

WHEEL_NAME="@WHEEL_NAME@"
WHEEL_SHA256="@WHEEL_SHA256@"

PYTHON="${PYTHON:-python3}"
MIN_MINOR=12
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APP_DIR="$DATA_HOME/cvss"
VENV_DIR="$APP_DIR/venv"
BIN_DIR="$HOME/.local/bin"
MAN_DIR="$DATA_HOME/man/man1"

usage() {
    echo "Usage: sh $(basename "$0") [--uninstall]"
    echo "  (no option)   install or upgrade the cvss command for the current user"
    echo "  --uninstall   remove the command, the man page and the private environment"
}

fail() {
    echo "installer: $*" >&2
    exit 1
}

# True when $1 is a link that points into our private environment.
is_ours() {
    [ -L "$1" ] && case "$(readlink "$1")" in "$VENV_DIR"/*) return 0 ;; esac
    return 1
}

check_python() {
    command -v "$PYTHON" >/dev/null 2>&1 || fail "$PYTHON not found. Install Python 3.$MIN_MINOR or newer (Debian/Ubuntu: sudo apt install python3 python3-venv)."
    "$PYTHON" -c "import sys; sys.exit(0 if sys.version_info >= (3, $MIN_MINOR) else 1)" ||
        fail "cvss needs Python 3.$MIN_MINOR or newer ($PYTHON is older)."
    "$PYTHON" -c "import venv, ensurepip" 2>/dev/null ||
        fail "the Python venv module is missing (Debian/Ubuntu: sudo apt install python3-venv)."
}

check_targets() {
    for target in "$BIN_DIR/cvss" "$MAN_DIR/cvss.1"; do
        if { [ -e "$target" ] || [ -L "$target" ]; } && ! is_ours "$target"; then
            fail "$target already exists and was not installed by this script. Not overwriting it."
        fi
    done
}

check_payload() {
    case "$WHEEL_NAME" in
        @*) fail "this is the installer template, not a built installer. Run ./build.sh and use the file it puts in dist/." ;;
    esac
    [ -f "$0" ] || fail "run this file directly (sh <file>), not through a pipe: the wheel is stored inside it."
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

# Copy the wheel stored after the marker line into $1 and check it is intact.
extract_wheel() {
    marker_line=$(grep -a -n '^__PAYLOAD_BELOW__$' "$0" | head -n 1 | cut -d: -f1)
    [ -n "$marker_line" ] || fail "the wheel is missing from this file."
    tail -n +"$((marker_line + 1))" "$0" >"$1"
    [ "$(sha256_of "$1")" = "$WHEEL_SHA256" ] || fail "the wheel inside this file is damaged (checksum mismatch). Copy or download it again."
}

install() {
    check_python
    check_targets
    check_payload

    workdir=$(mktemp -d)
    trap 'rm -rf "$workdir"' EXIT
    extract_wheel "$workdir/$WHEEL_NAME"

    mkdir -p "$APP_DIR" "$BIN_DIR" "$MAN_DIR"
    rm -rf "$VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --no-index --no-deps "$workdir/$WHEEL_NAME" || fail "pip could not install the wheel."

    ln -sf "$VENV_DIR/bin/cvss" "$BIN_DIR/cvss"
    ln -sf "$VENV_DIR/share/man/man1/cvss.1" "$MAN_DIR/cvss.1"
    "$BIN_DIR/cvss" --help >/dev/null || fail "the installed command does not run."

    echo "Installed: $BIN_DIR/cvss"
    echo "Man page:  $MAN_DIR/cvss.1  (try: man cvss)"
    case ":$PATH:" in
        *":$BIN_DIR:"*) ;;
        *) echo "Note: $BIN_DIR is not in your PATH. Add it with: export PATH=\"$BIN_DIR:\$PATH\"" ;;
    esac
}

uninstall() {
    removed=0
    for target in "$BIN_DIR/cvss" "$MAN_DIR/cvss.1"; do
        if is_ours "$target"; then
            rm -f "$target"
            echo "Removed $target"
            removed=1
        fi
    done
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        echo "Removed $VENV_DIR"
        removed=1
    fi
    rmdir "$APP_DIR" 2>/dev/null || true
    [ "$removed" -eq 1 ] || echo "Nothing to remove."
}

case "${1:-}" in
    "") install ;;
    --uninstall) uninstall ;;
    -h | --help) usage ;;
    *)
        usage >&2
        exit 2
        ;;
esac
exit 0
__PAYLOAD_BELOW__
