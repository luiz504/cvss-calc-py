# PYT-CVSS

A **CVSS v3.1 base score calculator** in Python, with a terminal mode and a browser UI.

Final project for the **Python Scripting** course (PUCPR Cybersecurity postgrad, Turma U).

> **Status:** work in progress. Tooling is set up; the calculator is being built step by step. Items marked _(planned)_ do not work yet.

## Goal

From the eight CVSS v3.1 base metrics, calculate the **base score** (0.0 to 10.0), the **severity** (None, Low, Medium, High, Critical) and the **vector string**. Both modes share the same scoring code, so they always agree.

| Mode | Command | What it is |
| --- | --- | --- |
| Terminal _(planned)_ | `python main.py cli` | Interactive prompts, or `--vector` for a one-shot run |
| Browser _(planned)_ | `python main.py web` | Local web page, standard library only |

Scope: base score only (no temporal or environmental scores). The rules, formulas and reference vectors are in [docs/domain.md](docs/domain.md).

## Requirements

- Python 3.12 or newer
- No runtime dependencies (standard library only)
- Dev tools, installed by `make install`: `pytest`, `pytest-watcher`, `ruff`

## Running _(planned)_

On any OS:

```bash
python main.py cli
python main.py web
```

With `make` (Linux/macOS): `make run-cli` (`make run-web` is planned).

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

- The web mode listens on `127.0.0.1` only, validates every input against an allowlist, and limits request size.
- Tests and examples use fictional data only. Keep this repository **private**.

## Docs

- [docs/domain.md](docs/domain.md): CVSS definitions, metric weights, formulas, severity bands, reference vectors
- [docs/design.md](docs/design.md): API of the core, module responsibilities, web contract, build order
- [docs/references.md](docs/references.md): specification, calculators, Python and tooling links
