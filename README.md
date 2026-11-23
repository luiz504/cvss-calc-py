# PYT-CVSS

A **CVSS v3.1 base score calculator** in Python, for the terminal: build it once on the development machine, then install the `cvss` command on any target from one installer file.

Final project for the **Python Scripting** course (PUCPR Cybersecurity postgrad, Turma U).

| | Where | What it needs |
| --- | --- | --- |
| [Development](#development) | the developer's machine | Python 3.12+ with `venv`, the network once |
| [Build](#build) | the developer's machine | the same, nothing more; produces the artifacts |
| [Artifacts](#artifacts-and-installation-per-target) | each target machine | depends on the target (the standalone one needs no Python) |

**Quick start.** Build once on the development machine, install on the target, uninstall when you are done:

```bash
./build-binary.sh                                        # on the dev machine: writes dist/cvss-<version>-linux-x86_64-installer.sh
sh cvss-<version>-linux-x86_64-installer.sh              # on the target (Linux x86_64, only sh and tar needed): install
cvss -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H     # use it
sh cvss-<version>-linux-x86_64-installer.sh --uninstall  # uninstall (lost the file? see Uninstall below)
```

Release notes: [CHANGELOG.md](CHANGELOG.md).

## Development

Everything that needs `venv`, `pip` or the network lives here, on the developer's machine, and nowhere else.

**Requirements**

| Need | Why |
| --- | --- |
| Python 3.12 or newer, with the `venv` module (Debian/Ubuntu: `sudo apt install python3 python3-venv`) | runs the project and the tests; the build scripts create a throwaway virtual environment |
| network access (once per install or build) | `pip` downloads the dev tools, the build tool (`setuptools`) and PyInstaller |
| `git` | version control and tags |
| `make` (optional; Debian/Ubuntu: `sudo apt install make`) | only shortcuts for the commands below; everything also works without it |

The program itself has no runtime dependencies (standard library only). The dev tools are `pytest`, `pytest-watcher` and `ruff`, pinned in `requirements-dev.txt`; the tests run offline.

**Commands**

| Command | What it does |
| --- | --- |
| `make help` | list all commands |
| `make install` | create `.venv` and install the dev tools |
| `make run-cli` | run the interactive mode from the source folder |
| `make test` / `make watch` | run the tests once / on every save |
| `make lint` / `make lint-fix` | ruff check (read-only) / ruff check with autofix |
| `make format` / `make format-check` | ruff format (rewrites files) / format check (read-only) |
| `make check` | pre-commit gate: `lint`, `format-check` and `test` (read-only) |
| `make build-binary` / `make build` | build the artifacts (see Build) |
| `make clean` | delete `.venv`, caches, `build/` and `dist/` |

Without `make`, run the same things from the virtual environment, for example `.venv/bin/python -m pytest`, or `python3 main.py` to run the program straight from the source folder (this needs only Python 3.12).

Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## Build

The build runs **on the development machine**, takes seconds, and writes its result to `dist/` (git-ignored). The version comes from `pyproject.toml`. Both scripts work inside a throwaway virtual environment and leave only `dist/` behind, so they never touch the system Python (a bare system with no `pip` is fine).

**This version has a single binary target: Linux x86_64.** The standalone installer is built for the CPU and system of the machine that builds it, so build it on an x86_64 Linux; a build for another CPU or system would have to run on that CPU or system.

| Command | Produces | Target | Builder needs |
| --- | --- | --- | --- |
| `./build-binary.sh` (or `make build-binary`) | `dist/cvss-<version>-linux-x86_64-installer.sh` | Linux x86_64 only | Python 3.12+ with `venv`, network once (PyInstaller 6.22.3 is downloaded) |
| `./build.sh` (or `make build`) | `dist/cvss-<version>-installer.sh` | any system with Python 3.12+ (tested on Linux) | Python 3.12+ with `venv`, network once (`setuptools` is downloaded) |

Before building a version, run `make check`. Build the standalone installer on the **oldest Linux you want to support**: the program inside is linked against the glibc of the build machine. (A build made on glibc 2.43 did run on Ubuntu 24.04, glibc 2.39, in our test, but that is not guaranteed.)

Each artifact is **one self-contained file** with its SHA-256 inside. The standalone one carries a ready-to-run `cvss` program and the man page; the Python one carries the project as a wheel. Copy the file to the target and run it there; the build machine and the target do not need to be the same.

## Artifacts and installation per target

Each installer installs for the **current user only**: no `sudo`, no network, no source folder. Both put the command in `~/.local/bin` and the man page in `~/.local/share/man`, and both refuse to overwrite a `cvss` they did not install. Only one of the two can be installed at a time: uninstall the first before using the second.

| Artifact | Target | Requirements on the target |
| --- | --- | --- |
| `cvss-<version>-linux-x86_64-installer.sh` | Linux x86_64 | `sh`, `tar` with gzip, and the standard tools every Linux has (`grep`, `tail`, `head`, `cut`, `mktemp`, `sha256sum`, `readlink`, `ln`, `cp`, `chmod`, `uname`). **No Python, no `venv`, no network.** |
| `cvss-<version>-installer.sh` | any system with Python (tested on Linux) | `sh`, Python 3.12+ **with the `venv` module** (Debian/Ubuntu: `sudo apt install python3 python3-venv`). No network. |
| the source folder | any system with Python | Python 3.12+ only, no install |

### Standalone installer (Linux x86_64)

```bash
sh cvss-<version>-linux-x86_64-installer.sh             # install, or upgrade when run again
cvss --help
man cvss
sh cvss-<version>-linux-x86_64-installer.sh --uninstall # remove everything it installed
```

- Installs the program into `~/.local/share/cvss/` and links `~/.local/bin/cvss` and `~/.local/share/man/man1/cvss.1` to it.
- Checks its own SHA-256 before installing, and stops with a clear message on another CPU type, on a system that is not Linux, or when the file was damaged.
- Verified: a standalone program built on one Ubuntu ran on Ubuntu 24.04 x86_64 with no Python installed.

### Python installer (any system with Python 3.12+ and `venv`)

```bash
sh cvss-<version>-installer.sh              # install, or upgrade when run again
cvss --help
man cvss
sh cvss-<version>-installer.sh --uninstall  # remove everything it installed
```

- Creates a private virtual environment in `~/.local/share/cvss/venv`, installs the wheel into it offline, and links `~/.local/bin/cvss` and the man page.
- Stops with a clear message when Python is missing, older than 3.12, or has no `venv` module (it then names the package to install).
- The file is small and its shell part is plain text, so it can be read before running.

### Running from the source folder (no install)

```bash
python3 main.py
python3 main.py -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H -c
man -l man/cvss.1
```

On Linux there is no bare `python` command: use `python3`.

### After installing: the `PATH`

`~/.local/bin` must be in your `PATH` for `cvss` to be found. On a fresh Debian/Ubuntu it is added at your **next login** (the default `~/.profile` adds it when the folder exists), so either open a new login shell or run, in the current shell:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

and add that line to `~/.bashrc` (bash) or `~/.zshrc` (zsh) to keep it. The installer prints a note when `~/.local/bin` is missing from your `PATH`. `man cvss` works the same way: `~/.local/share/man` is picked up automatically by `man` once it exists.

## Uninstall

### With the installer file

Run the same file you installed from, with `--uninstall`:

```bash
sh cvss-<version>-linux-x86_64-installer.sh --uninstall    # the standalone one
sh cvss-<version>-installer.sh --uninstall                 # the Python one
```

It removes the command, the man page and the program files, only the ones it installed, and tells you what it removed (or `Nothing to remove.`).

### By hand (lost the installer file)

This works for **both** installers, because both put the same things in the same places. First check that the `cvss` you have is the one this project installed:

```bash
ls -l ~/.local/bin/cvss
```

If the link points into `~/.local/share/cvss/` (for example `-> ~/.local/share/cvss/cvss` for the standalone one, or `-> ~/.local/share/cvss/venv/bin/cvss` for the Python one), it is ours. If it points anywhere else, it is another program: do not delete it. Then remove everything:

```bash
rm -f ~/.local/bin/cvss ~/.local/share/man/man1/cvss.1
rm -rf ~/.local/share/cvss
rm -rf "${TMPDIR:-/tmp}/cvss-calc"      # optional: the folder where -c writes the chart
```

If you set `XDG_DATA_HOME`, use it instead of `~/.local/share` in the lines above.

### Check that it is gone

```bash
command -v cvss || echo "cvss: not found"    # prints "cvss: not found"
man cvss                                     # prints "No manual entry for cvss"
ls ~/.local/share/cvss                       # prints "No such file or directory"
```

Open a new shell first if `command -v` still finds it: the shell remembers command locations. The installers **never edit your shell files**, so a `PATH` line you added yourself stays; remove it by hand if you do not want it. Installing again later is just running an installer again.

## Troubleshooting

| What you see | What it means and what to do |
| --- | --- |
| `cvss: command not found` after installing | `~/.local/bin` is not in your `PATH` yet: open a new login shell, or run `export PATH="$HOME/.local/bin:$PATH"` (see After installing) |
| `installer: ... already exists and was not installed by this script` | another `cvss` is in the way. If it is the other installer's, uninstall it first; if it is something else, move it away. The installer never overwrites it |
| `installer: ... damaged (checksum mismatch)` | the file was cut or changed while copying: copy or download it again |
| `installer: this installer was built for <cpu>, this machine is <cpu>` | the standalone installer is for Linux x86_64 only: use the Python installer, or build it on that machine |
| `installer: the Python venv module is missing` | Python installer only: `sudo apt install python3-venv` (Debian/Ubuntu), or use the standalone installer, which needs no Python |
| `installer: cvss needs Python 3.12 or newer` | Python installer only: use a newer Python (`PYTHON=python3.13 sh cvss-<version>-installer.sh`), or the standalone installer |
| `GLIBC_2.xx not found` when running the standalone `cvss` | it was built on a newer Linux than this one: build it on the oldest Linux you want to support |
| `build.sh: could not create a virtual environment` | on the build machine: `sudo apt install python3-venv` |
| `man cvss`: `No manual entry` | open a new shell, or read it directly: `man -l ~/.local/share/man/man1/cvss.1` |
| strange characters such as `^[[1m` in the output | the colors are on and your viewer does not render them: use `NO_COLOR=1 cvss ...`, or `less -R` for pagers |
| `Chart saved:` shows a path but you cannot find the file | `-c` writes to the temp folder (`/tmp/cvss-calc/cvss-score.svg`); use `-o FILE` to choose where |

## Usage

| Mode | Command | What it is |
| --- | --- | --- |
| Interactive | `cvss` | Asks the 8 metrics one by one, repeating a question until the answer is valid |
| One-shot | `cvss -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | Scores a vector string and exits (code 1 if the vector is invalid) |

Both modes accept the chart options below. Scope: base score only (no temporal or environmental scores). The rules, formulas and reference vectors are in [docs/domain.md](docs/domain.md).

```text
usage: cvss [-h] [-v VECTOR] [-c] [-o FILE]

  -h, --help           show this help message and exit
  -v, --vector VECTOR  score this CVSS:3.1 vector and exit
  -c, --chart          also write the SVG chart to the temp folder and print its path
  -o, --output FILE    write the SVG chart to FILE (a file, not a folder; overwritten if it exists; implies --chart)
```

| Exit code | Meaning |
| --- | --- |
| 0 | done |
| 1 | the vector is invalid, or the chart could not be written (the score is still printed) |
| 2 | usage error, or an unusable `-o` path (checked before anything runs) |

### Chart

`-c` or `-o` writes an SVG with three bars (**Base**, **Impact**, **Exploitability**, scale 0 to 10), each colored by severity band (0 to 3.9 green, 4 to 6.9 blue, 7 to 8.9 orange, 9 to 10 red), the value above each bar and the vector at the bottom. A negative raw impact (scope changed, no C/I/A impact) is shown as 0.

| Command | Where the file goes |
| --- | --- |
| `-c` | `<system temp folder>/cvss-calc/cvss-score.svg` (on Linux `/tmp/cvss-calc/cvss-score.svg`); the next run overwrites it |
| `-o FILE` | exactly `FILE`, overwritten if it exists; the folder must already exist |

Example (the path is printed at the end; open the file in a browser):

```text
$ cvss -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H -o /tmp/cvss.svg
Score: 9.8
Severity: Critical
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Generating chart...
Chart saved: /tmp/cvss.svg
```

If the file cannot be written, the score is still shown, the error goes to stderr (`cvss: error: cannot write the chart: ...`) and the exit code is 1.

### Color

The output is always colored, to keep it easy to read: the labels are bold and the severity follows the same bands as the chart, **Low** green, **Medium** yellow, **High** red, **Critical** white on red (and **None** dim). Wrong answers and errors are red, the step in each prompt is dim, and `Chart saved:` is green.

There is no option for it. Colors stay on even when the output is piped, so use `less -R` to read colored output in a pager. Two standard cases switch them off by themselves: a non-empty `NO_COLOR` environment variable ([no-color.org](https://no-color.org)), for example `NO_COLOR=1 cvss -v ... | grep Score`, and `TERM=dumb`.

## Class topics covered

| Class topic | Where it appears |
| --- | --- |
| expressions, number and string operators | `core.py`: the score formulas and `roundup`; `parse_vector` splits and checks strings; `chart.py` builds the SVG text |
| conditionals | `calculate_base_score` (scope and impact rules), `rate_severity`, `color_for_score` |
| exceptions / error handling | `CvssError`, `try/except` in `run_vector`, and `try/except OSError` in `save_chart` |
| loops, input until valid | the `while True` loop for each metric in `cli.py`; the loop that draws the three bars in `chart.py` |
| collections: dict, tuple, list | metrics are a `dict`; `calculate_subscores` returns a `tuple`; `build_svg` collects the SVG lines in a `list` |
| functions | one small function per rule in `core.py`, `cli.py` and `chart.py` |
| command-line arguments | `argparse` in `cvss/app.py` (`-v`, `-c`, `-o`, `-h`) |
| files and paths | `pathlib.Path`, `tempfile`, `write_chart` and the early check of the `-o` path (`find_output_problem`) |
| environment variables | `colors.py`: `os.environ` (`NO_COLOR`, `TERM`) and ANSI escape codes |
| dataclasses | frozen `FormulaConstants`, `ChartColors` and `ChartConstants` hold every named constant |
| packaging and build | `pyproject.toml` (console script `cvss`), `build.sh` and `build-binary.sh`, and the two one-file installers |
| external modules | `argparse`, `sys`, `os`, `pathlib`, `tempfile`; `pytest`, `ruff` and PyInstaller as build-time tools |

## Security notes

- Every input is validated against the allowed values before it is used. The program makes no network calls.
- Only validated metric letters reach the SVG text, so nothing typed by the user is written into the file unescaped.
- The `-o` path is checked before anything runs (missing folder, a directory, no permission), and a write error is reported instead of crashing. The default chart goes to the system temp folder, never into the project.
- The installers work only inside your home folder, never use `sudo`, refuse to overwrite a `cvss` file they did not install, and check the SHA-256 of the program they carry (that detects a damaged copy; the files are not signed). The standalone program is built from this source, so read the source rather than the binary.
- Tests and examples use fictional data only. Keep this repository **private**.

## Docs

- [CHANGELOG.md](CHANGELOG.md): what changed in each release (one section per tag)
- [docs/domain.md](docs/domain.md): CVSS definitions, metric weights, formulas, severity bands, reference vectors
- [docs/roadmap.md](docs/roadmap.md): what comes next (temporal, environmental, overall, the rest of the chart's labels, translation), as a checklist
- [docs/design.md](docs/design.md): API of the core and the chart, module responsibilities, packaging, build order
- [docs/references.md](docs/references.md): specification, calculators, Python and tooling links
- `man cvss` (source in [man/cvss.1](man/cvss.1)): the manual page
