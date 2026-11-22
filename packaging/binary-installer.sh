#!/bin/sh
# cvss installer (no Python needed): ONE self-contained file made by ./build-binary.sh. A tarball holding the cvss
# program (a standalone executable) and its man page is appended after the marker line at the bottom, so installing
# needs only sh and tar: no Python, no venv, no pip, no network, no sudo.
#
#   sh cvss-<version>-linux-<arch>-installer.sh              install or upgrade for the current user
#   sh cvss-<version>-linux-<arch>-installer.sh --uninstall  remove everything it installed
#
# It puts the program in ~/.local/share/cvss and links it into ~/.local/bin and the man page into ~/.local/share/man.

set -eu

PAYLOAD_SHA256="@PAYLOAD_SHA256@"
PAYLOAD_ARCH="@PAYLOAD_ARCH@"

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APP_DIR="$DATA_HOME/cvss"
BIN_DIR="$HOME/.local/bin"
MAN_DIR="$DATA_HOME/man/man1"

usage() {
    echo "Usage: sh $(basename "$0") [--uninstall]"
    echo "  (no option)   install or upgrade the cvss command for the current user"
    echo "  --uninstall   remove the command, the man page and the program files"
}

fail() {
    echo "installer: $*" >&2
    exit 1
}

# True when $1 is a link that points into our own folder.
is_ours() {
    [ -L "$1" ] && case "$(readlink "$1")" in "$APP_DIR"/*) return 0 ;; esac
    return 1
}

check_targets() {
    for target in "$BIN_DIR/cvss" "$MAN_DIR/cvss.1"; do
        if { [ -e "$target" ] || [ -L "$target" ]; } && ! is_ours "$target"; then
            fail "$target already exists and was not installed by this script. Not overwriting it (if it is another cvss installation, uninstall that one first)."
        fi
    done
}

check_payload() {
    case "$PAYLOAD_ARCH" in
        @*) fail "this is the installer template, not a built installer. Run ./build-binary.sh and use the file it puts in dist/." ;;
    esac
    [ -f "$0" ] || fail "run this file directly (sh <file>), not through a pipe: the program is stored inside it."
}

check_platform() {
    [ "$(uname -s)" = "Linux" ] || fail "this installer is for Linux ($(uname -s) found)."
    [ "$(uname -m)" = "$PAYLOAD_ARCH" ] || fail "this installer was built for $PAYLOAD_ARCH, this machine is $(uname -m)."
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

# Copy the tarball stored after the marker line into $1 and check it is intact.
extract_payload() {
    marker_line=$(grep -a -n '^__PAYLOAD_BELOW__$' "$0" | head -n 1 | cut -d: -f1)
    [ -n "$marker_line" ] || fail "the program is missing from this file."
    tail -n +"$((marker_line + 1))" "$0" >"$1"
    [ "$(sha256_of "$1")" = "$PAYLOAD_SHA256" ] || fail "the program inside this file is damaged (checksum mismatch). Copy or download it again."
}

install() {
    check_targets
    check_payload
    check_platform

    workdir=$(mktemp -d)
    trap 'rm -rf "$workdir"' EXIT
    extract_payload "$workdir/payload.tar.gz"
    tar -xzf "$workdir/payload.tar.gz" -C "$workdir"

    mkdir -p "$APP_DIR" "$BIN_DIR" "$MAN_DIR"
    rm -f "$APP_DIR/cvss" "$APP_DIR/cvss.1"
    cp "$workdir/cvss" "$APP_DIR/cvss"
    cp "$workdir/cvss.1" "$APP_DIR/cvss.1"
    chmod 755 "$APP_DIR/cvss"
    chmod 644 "$APP_DIR/cvss.1"

    ln -sf "$APP_DIR/cvss" "$BIN_DIR/cvss"
    ln -sf "$APP_DIR/cvss.1" "$MAN_DIR/cvss.1"
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
    for file in "$APP_DIR/cvss" "$APP_DIR/cvss.1"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            echo "Removed $file"
            removed=1
        fi
    done
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
