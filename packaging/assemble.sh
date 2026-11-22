#!/bin/sh
# Turn a program and its man page into ONE installer file.
#
#   sh packaging/assemble.sh BINARY MANPAGE OUTPUT
#
# OUTPUT is binary-installer.sh with a tarball of BINARY (named cvss) and MANPAGE (named cvss.1) appended, and the
# tarball's SHA-256 and the CPU type written into its header. PAYLOAD_ARCH overrides the CPU type (used by the tests).
# Needs only sh, tar, gzip, sed, cat and sha256sum.

set -eu

[ "$#" -eq 3 ] || {
    echo "Usage: sh packaging/assemble.sh BINARY MANPAGE OUTPUT" >&2
    exit 2
}
binary="$1"
manpage="$2"
output="$3"
here=$(cd "$(dirname "$0")" && pwd)
arch="${PAYLOAD_ARCH:-$(uname -m)}"

if command -v sha256sum >/dev/null 2>&1; then
    sha256_of() { sha256sum "$1" | cut -d' ' -f1; }
else
    sha256_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir "$work/payload"
cp "$binary" "$work/payload/cvss"
cp "$manpage" "$work/payload/cvss.1"
chmod 755 "$work/payload/cvss"
tar -cf - -C "$work/payload" cvss cvss.1 | gzip -n >"$work/payload.tar.gz"

sed -e "s|@PAYLOAD_SHA256@|$(sha256_of "$work/payload.tar.gz")|" -e "s|@PAYLOAD_ARCH@|$arch|" "$here/binary-installer.sh" >"$output"
cat "$work/payload.tar.gz" >>"$output"
chmod +x "$output"
