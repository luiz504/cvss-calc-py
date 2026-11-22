#!/bin/sh
# Build the one-file installer: dist/cvss-<version>-installer.sh
#
#   ./build.sh
#
# Needs python3 with the venv module (Debian/Ubuntu: sudo apt install python3 python3-venv) and the network once
# (pip, which the venv brings, downloads the build tool, setuptools). No system pip, no make.
# The result needs only Python 3.12+ with venv to install, and no network.

set -eu

PYTHON="${PYTHON:-python3}"
cd "$(dirname "$0")"

fail() {
    echo "build.sh: $*" >&2
    exit 1
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

command -v "$PYTHON" >/dev/null 2>&1 || fail "$PYTHON not found."

rm -rf build dist ./*.egg-info
mkdir -p build/wheel dist
# Build inside a throwaway virtual environment: a bare system has no pip, and this never touches the system Python.
"$PYTHON" -m venv build/venv || fail "could not create a virtual environment (Debian/Ubuntu: sudo apt install python3-venv)."
build/venv/bin/pip wheel . --no-deps --quiet --wheel-dir build/wheel || fail "pip could not build the wheel (is the network up? pip downloads setuptools)."

set -- build/wheel/*.whl
[ "$#" -eq 1 ] || fail "expected exactly one wheel in build/wheel."
wheel="$1"
wheel_name=$(basename "$wheel")
version=$(echo "$wheel_name" | cut -d- -f2)
installer="dist/cvss-$version-installer.sh"

sed -e "s|@WHEEL_NAME@|$wheel_name|" -e "s|@WHEEL_SHA256@|$(sha256_of "$wheel")|" packaging/installer.sh >"$installer"
cat "$wheel" >>"$installer"
chmod +x "$installer"
rm -rf build ./*.egg-info

echo "Built $installer ($(wc -c <"$installer") bytes)"
echo "Install it with: sh $installer"
