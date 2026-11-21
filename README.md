# PYT-CVSS

A **CVSS v3.1 base score calculator** in Python, for the terminal.

Final project for the **Python Scripting** course (PUCPR Cybersecurity postgrad, Turma U).

## Goal

From the eight CVSS v3.1 base metrics, calculate the **base score** (0.0 to 10.0), the **severity** (None, Low, Medium, High, Critical) and the **vector string**. The scoring code is separate from the terminal code.

| Mode | Command | What it is |
| --- | --- | --- |
| Interactive | `python main.py cli` | Asks the 8 metrics one by one, repeating a question until the answer is valid |
| One-shot | `python main.py cli --vector CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | Scores a vector string and exits (code 1 if the vector is invalid) |

Scope: base score only (no temporal or environmental scores). The rules, formulas and reference vectors are in [docs/domain.md](docs/domain.md).

## Requirements

- Python 3.12 or newer
- No runtime dependencies (standard library only)
- Dev tools, installed by `make install`: `pytest`, `pytest-watcher`, `ruff`

## Running

On any OS:

```bash
python main.py cli
```

With `make` (Linux/macOS): `make run-cli`.

On Linux there is no bare `python` command: use `make run-cli`, run `source .venv/bin/activate` first, or use `python3`.

## Class topics covered

| Class topic | Where it appears |
| --- | --- |
| expressions, number and string operators | `core.py`: the score formulas and `roundup`; `parse_vector` splits and checks strings |
| conditionals | `calculate_base_score` (scope and impact rules) and `rate_severity` |
| exceptions / error handling | `CvssError`, and `try/except` in `run_vector` |
| loops, input until valid | the `while True` loop for each metric in `cli.py` |
| collections: dict, tuple | metrics are a `dict`; `calculate_subscores` returns a `tuple` |
| functions | one small function per rule in `core.py` and `cli.py` |
| external modules | `sys` in `main.py`; `pytest` and `ruff` as dev tools |

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
- Tests and examples use fictional data only. Keep this repository **private**.

## Docs

- [docs/domain.md](docs/domain.md): CVSS definitions, metric weights, formulas, severity bands, reference vectors
- [docs/design.md](docs/design.md): API of the core, module responsibilities, build order
- [docs/references.md](docs/references.md): specification, calculators, Python and tooling links
