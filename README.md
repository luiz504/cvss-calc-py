# PYT-CVSS

A **CVSS v3.1 base score calculator** in Python, for the terminal.

Final project for the **Python Scripting** course (PUCPR Cybersecurity postgrad, Turma U).

## Goal

From the eight CVSS v3.1 base metrics, calculate the **base score** (0.0 to 10.0), the **severity** (None, Low, Medium, High, Critical) and the **vector string**, and optionally draw them as an **SVG chart**. The scoring code is separate from the terminal code.

| Mode | Command | What it is |
| --- | --- | --- |
| Interactive | `python main.py` | Asks the 8 metrics one by one, repeating a question until the answer is valid |
| One-shot | `python main.py -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | Scores a vector string and exits (code 1 if the vector is invalid) |

Both modes accept the chart options below. Scope: base score only (no temporal or environmental scores). The rules, formulas and reference vectors are in [docs/domain.md](docs/domain.md).

## Options

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

## Chart

`-c` or `-o` writes an SVG with three bars (**Base**, **Impact**, **Exploitability**, scale 0 to 10), each colored by severity band (0 to 3.9 green, 4 to 6.9 blue, 7 to 8.9 orange, 9 to 10 red), the value above each bar and the vector at the bottom. A negative raw impact (scope changed, no C/I/A impact) is shown as 0.

| Command | Where the file goes |
| --- | --- |
| `-c` | `<system temp folder>/cvss-calc/cvss-score.svg` (on Linux `/tmp/cvss-calc/cvss-score.svg`); the next run overwrites it |
| `-o FILE` | exactly `FILE`, overwritten if it exists; the folder must already exist |

Example (the path is printed at the end; open the file in a browser):

```text
$ python main.py -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H -o /tmp/cvss.svg
Score: 9.8
Severity: Critical
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Generating chart...
Chart saved: /tmp/cvss.svg
```

If the file cannot be written, the score is still shown, the error goes to stderr (`cvss: error: cannot write the chart: ...`) and the exit code is 1.

## Requirements

- Python 3.12 or newer
- No runtime dependencies (standard library only)
- Dev tools, installed by `make install`: `pytest`, `pytest-watcher`, `ruff`

## Running

On any OS:

```bash
python main.py
python main.py -v CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H -c
```

With `make` (Linux/macOS): `make run-cli` starts the interactive mode.

On Linux there is no bare `python` command: use `make run-cli`, run `source .venv/bin/activate` first, or use `python3`.

## Class topics covered

| Class topic | Where it appears |
| --- | --- |
| expressions, number and string operators | `core.py`: the score formulas and `roundup`; `parse_vector` splits and checks strings; `chart.py` builds the SVG text |
| conditionals | `calculate_base_score` (scope and impact rules), `rate_severity`, `color_for_score` |
| exceptions / error handling | `CvssError`, `try/except` in `run_vector`, and `try/except OSError` in `save_chart` |
| loops, input until valid | the `while True` loop for each metric in `cli.py`; the loop that draws the three bars in `chart.py` |
| collections: dict, tuple, list | metrics are a `dict`; `calculate_subscores` returns a `tuple`; `build_svg` collects the SVG lines in a `list` |
| functions | one small function per rule in `core.py`, `cli.py` and `chart.py` |
| command-line arguments | `argparse` in `main.py` (`-v`, `-c`, `-o`, `-h`) |
| files and paths | `pathlib.Path`, `tempfile`, `write_chart` and the early check of the `-o` path (`find_output_problem`) |
| dataclasses | frozen `FormulaConstants`, `ChartColors` and `ChartConstants` hold every named constant |
| external modules | `argparse`, `sys`, `pathlib`, `tempfile`; `pytest` and `ruff` as dev tools |

## Development

| Command | What it does |
| --- | --- |
| `make help` | list all commands |
| `make install` | create `.venv` and install the dev tools |
| `make test` / `make watch` | run the tests once / on every save |
| `make lint` / `make lint-fix` | ruff check (read-only) / ruff check with autofix |
| `make format` / `make format-check` | ruff format (rewrites files) / format check (read-only) |
| `make check` | pre-commit gate: `lint`, `format-check` and `test` (read-only) |
| `make clean` | delete `.venv` and caches |

Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## Security notes

- Every input is validated against the allowed values before it is used. The program makes no network calls.
- Only validated metric letters reach the SVG text, so nothing typed by the user is written into the file unescaped.
- The `-o` path is checked before anything runs (missing folder, a directory, no permission), and a write error is reported instead of crashing. The default chart goes to the system temp folder, never into the project.
- Tests and examples use fictional data only. Keep this repository **private**.

## Docs

- [docs/domain.md](docs/domain.md): CVSS definitions, metric weights, formulas, severity bands, reference vectors
- [docs/design.md](docs/design.md): API of the core and the chart, module responsibilities, build order
- [docs/references.md](docs/references.md): specification, calculators, Python and tooling links
