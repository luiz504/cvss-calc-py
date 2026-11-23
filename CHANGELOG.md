# Changelog

All notable changes to PYT-CVSS, one section per release (each one is a git tag). The format follows
[Keep a Changelog](https://keepachangelog.com/) and the versions follow [Semantic Versioning](https://semver.org/).

**Releasing:** write the changes under *Unreleased* as you make them. To release, rename that section to the new
version and date, set the same `version` in `pyproject.toml` (tests check that this file has an entry for it and that the man page header shows it too: `man/cvss.1`, first line), commit,
then tag it (`git tag -a vX.Y.Z`).

## [Unreleased]

## [1.1.1] - 2026-11-22

Tag `v1.1.1`. A standalone installer that needs no Python on the target, always-on colors, a build that works on a bare
system, and the README rewritten around install, uninstall and troubleshooting.

### Added

- **Standalone installer** (`build-binary.sh`, `packaging/assemble.sh`, `packaging/binary-installer.sh`): one file that
  carries a ready-to-run `cvss` program and the man page. The machine that installs it needs only `sh` and `tar`, no
  Python and no `venv`. Single binary target in this version: Linux x86_64. It checks its SHA-256, refuses another CPU
  type, never overwrites a `cvss` it did not install, and has `--uninstall`.
- **Colors**, always on: bold labels, a severity color (Low green, Medium yellow, High red, Critical white on red),
  red errors, dim prompt steps. `NO_COLOR` and `TERM=dumb` switch them off; the man page documents both.
- `make build-binary`; `make clean` now also removes `build/`, `dist/` and the egg-info folder.
- README: a quick start, how to uninstall (also by hand, when the installer file is gone), how to find out which
  installer put `cvss` there, and a troubleshooting table.
- `docs/roadmap.md`: the checklist for the next versions (temporal, environmental and overall scores, the rest of the
  chart's labels, translation) with the domain check.
- This changelog, and tests that fail when the version in `pyproject.toml` has no entry here or is not the one shown in
  the man page header.

### Changed

- The README is organised as development requirements, then the build (it runs on the development machine; this
  version has a single binary target, Linux x86_64), then the artifacts with their installation and requirements per
  target. The standalone installer is the recommended route; the Python installer stays as the alternative.
- Version set to `1.1.1` in `pyproject.toml` and in the man page header.

### Fixed

- The man page footer said `pyt-cvss 1.0.0` (it did so in `v1.1.0` too); it now shows the project version.
- `build.sh` builds in a throwaway virtual environment, so it works on a bare Debian/Ubuntu that has no `pip`; the
  message for a missing `venv` module now names the package to install.
- `build.sh` and `build-binary.sh` no longer delete `dist/`: building one used to remove the other's installer.
- The tests run the build scripts in a throwaway copy of the project; `make test` used to empty the real `dist/`.

## [1.1.0] - 2026-11-22

Tag `v1.1.0`. The first installable version.

### Added

- The `cvss` command: `pyproject.toml` with a console script (setuptools), so the project installs like any Python
  package.
- The manual page, `man cvss` (`man/cvss.1`); a test checks that it mentions every long option the parser has.
- `build.sh`: builds one installer file that carries the project as a wheel. Installing it is offline, creates a
  private virtual environment in `~/.local/share/cvss`, links the command and the man page into `~/.local`, checks its
  SHA-256, never overwrites a `cvss` it did not install, and has `--uninstall`. Needs Python 3.12+ with `venv`.

### Changed

- The command line moved into the package (`cvss/app.py`) so it can be installed; `main.py` stays as a four-line shim,
  so `python main.py` still works from the source folder.
- Version set to `1.1.0` in `pyproject.toml`.

## [1.0] - 2026-11-22

Tag `v1.0`. The first release: **the base score only**. Temporal, environmental and overall scores are not part of it.

### Added

- The **CVSS v3.1 base score** calculator: validation of the eight base metrics (missing and unknown metrics, wrong
  types, letters that are not allowed), `Roundup` as the specification's integer version, the exploitability and impact
  subscores (including the scope-changed rules), the base score (0.0 when there is no impact, capped at 10), the
  severity (None, Low, Medium, High, Critical) and the vector string, built and parsed.
- A terminal program with two modes: interactive (eight prompts that show the step and the group and repeat until the
  answer is valid) and one-shot (`-v`/`--vector`). Both print the score, the severity and the vector; the exit code is 1
  for an invalid vector.
- A command line like a Linux tool (`argparse`): `-v/--vector`, `-c/--chart`, `-o/--output FILE`, `-h/--help`; an unusable
  `-o` path (missing folder, a directory, no permission) is rejected before anything runs; exit codes 0, 1 and 2.
- An **SVG chart of the base scores** (Base, Impact, Exploitability, each colored by severity band, with its value and
  the vector; a negative impact is shown as 0), written to the temp folder with `-c` or to `FILE` with `-o`; write errors
  are reported without hiding the score.
- Documentation (domain, design, references, README), `make` shortcuts, `ruff` and `pytest` tooling.

[Unreleased]: https://github.com/luiz504/cvss-calc-py/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/luiz504/cvss-calc-py/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/luiz504/cvss-calc-py/compare/v1.0...v1.1.0
[1.0]: https://github.com/luiz504/cvss-calc-py/releases/tag/v1.0
