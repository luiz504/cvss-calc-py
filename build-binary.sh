#!/bin/sh
# Build the standalone installer: dist/cvss-<version>-linux-<cpu>-installer.sh
#
#   ./build-binary.sh
#
# The installer carries a standalone cvss executable (made with PyInstaller) and the man page, so the machine that
# installs it needs no Python at all, only sh and tar.
# THIS machine needs python3 with the venv module (Debian/Ubuntu: sudo apt install python3 python3-venv) and the
# network once (pip downloads PyInstaller). Build on the oldest Linux you want to support: the result runs on the same
# or a newer glibc, not an older one.

set -eu

PYTHON="${PYTHON:-python3}"
PYINSTALLER_VERSION="6.22.3"
cd "$(dirname "$0")"

fail() {
    echo "build-binary.sh: $*" >&2
    exit 1
}

command -v "$PYTHON" >/dev/null 2>&1 || fail "$PYTHON not found."

version=$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml | head -n 1)
[ -n "$version" ] || fail "could not read the version from pyproject.toml."
arch=$(uname -m)
installer="dist/cvss-$version-linux-$arch-installer.sh"

rm -rf build dist ./*.egg-info
mkdir -p build dist

# Build inside a throwaway virtual environment: a bare system has no pip, and this never touches the system Python.
"$PYTHON" -m venv build/venv || fail "could not create a virtual environment (Debian/Ubuntu: sudo apt install python3-venv)."
build/venv/bin/pip install --quiet "pyinstaller==$PYINSTALLER_VERSION" || fail "pip could not install PyInstaller (is the network up?)."
build/venv/bin/pyinstaller --onefile --name cvss --distpath build/bin --workpath build/work --specpath build --log-level WARN main.py ||
    fail "PyInstaller failed."

sh packaging/assemble.sh build/bin/cvss man/cvss.1 "$installer"
rm -rf build ./*.egg-info

echo "Built $installer ($(wc -c <"$installer") bytes)"
echo "Install it with: sh $installer"
