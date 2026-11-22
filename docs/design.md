# Design

Decisions for how the code is organised. The rules being implemented are in [domain.md](domain.md).

## Decisions

- Base score only (CVSS 3.1). No temporal or environmental scores.
- Metrics are plain `dict[str, str]` (e.g. `{"AV": "N", "AC": "L", ...}`), not a class. They serialize to JSON for free.
- `Roundup` follows the specification's integer version, not `ceil(x * 10) / 10`.
- English only, no translations in v1. Metrics and values are stored under stable uppercase keys (e.g. `ATTACK_VECTOR`, `NETWORK`), which the CLI shows as they are.
- Definitions and weights are separate tables: `BASE_METRICS` says which metrics and letters exist, `BASE_METRICS_WEIGHTS` holds the scoring numbers.
- The CLI contains **no scoring rules**. It calls `core`.
- The chart is plain SVG text built with the standard library (no plotting dependency). Building the text and writing the file are two separate functions.
- Command line like a Linux tool: no subcommand, interactive by default, `-v/--vector`, `-c/--chart`, `-o/--output FILE` (short and long forms), `argparse` for parsing and `--help`.
- Fail early: an unusable `-o` path is rejected before any prompt or score. Errors go to stderr, the exit code says what happened.

## `cvss/core.py` (pure: no I/O, no printing)

```text
BASE_METRICS                             # per metric: a label key, a group (EXPLOITABILITY | SCOPE | IMPACT) and its allowed values {letter: key}
BASE_METRICS_WEIGHTS                    # weights for the formula
PR_WEIGHTS_SCOPE_CHANGED                 # PR weights when the scope is changed
FORMULA                                  # frozen dataclass from formula.py: formula numbers, severity limits
validate_metrics(metrics) -> None        # raises CvssError
calculate_subscores(metrics) -> (exploitability, impact)   # unrounded
calculate_base_score(metrics) -> float   # validates, then computes (one decimal)
rate_severity(score) -> str             # None | Low | Medium | High | Critical
parse_vector(vector) -> dict[str, str]   # raises CvssError
build_vector(metrics) -> str             # "CVSS:3.1/AV:N/..."
```

- One error type: `CvssError(ValueError)`. Messages name the metric and the allowed values, e.g. `AV must be one of N, A, L, P (got "X")`. The CLI prints the message, so the wording lives in one place.
- The CLI prompts are generated from `BASE_METRICS`.

## `cvss/chart.py` (the SVG: text first, file second)

```text
COLORS, CHART                            # frozen dataclasses: band colors, sizes, offsets, default file name
color_for_score(score) -> str            # one color per severity band, limits come from FORMULA
build_svg(metrics) -> str                # pure: validates, then returns the SVG text
default_chart_path() -> Path             # <system temp folder>/cvss-calc/cvss-score.svg
write_chart(metrics, path=None) -> Path  # builds the text first, then writes it; OSError propagates
```

- Three bars, **Base**, **Impact**, **Exploitability**, on a 0 to 10 scale. The value is rounded once to one decimal and that single number drives the bar height, the color and the label.
- A negative raw impact (scope changed, no C/I/A impact) is shown as 0.
- `write_chart` creates only the default temp folder. An explicit path is written exactly where it points, so a missing folder is an error, never silently created.
- Invalid metrics raise `CvssError` before anything touches the disk.

## Modules

| Module | Responsibility |
| --- | --- |
| `formula.py` | named constants: formula numbers, severity limits, vector prefix |
| `base_metrics.py` | metric definitions and weights |
| `core.py` | scoring rules, validation, severity, vector build |
| `chart.py` | band colors, SVG text, writing the file |
| `cli.py` | prompts, loops until each answer is valid, printing; `finish_run` (result, then chart if requested) and `save_chart` (writes the chart, reports the path or the `OSError`) |
| `app.py` | the command line: `argparse` flags, early check of the `-o` path, `run()` (the console-script entry point), hands off to the interactive or one-shot mode |
| `main.py` (project root) | 4-line shim so `python main.py` still works from the source folder |

## Packaging

- `pyproject.toml` uses setuptools. `cvss = "cvss.app:run"` under `[project.scripts]` makes the installer create the `cvss` command.
- `man/cvss.1` is a hand-written man page, shipped as `share/man/man1/cvss.1` (`[tool.setuptools.data-files]`). The installer links it into `~/.local/share/man`, so `man cvss` works after the install.
- **Build**: `./build.sh` (or `make build`) runs `pip wheel` inside a throwaway venv (so a bare system without `python3-pip` works), then writes `dist/cvss-<version>-installer.sh`: the shell installer in `packaging/installer.sh` with the wheel appended after a marker line and its SHA-256 written into the header. Only the build needs the network (pip fetches `setuptools`) and `python3-venv`. `dist/` and `build/` are git-ignored.
- **Install**: `sh dist/cvss-<version>-installer.sh` needs only Python 3.12+ with `venv`, no network, no source folder, no make, no sudo. It verifies the checksum, creates a private venv in `~/.local/share/cvss`, installs the wheel with `pip --no-index --no-deps`, and links `cvss` into `~/.local/bin` and the man page into `~/.local/share/man`. `--uninstall` removes it. It refuses to overwrite a `cvss` it did not install. The program has no runtime dependencies.
- The checksum detects a damaged or truncated copy, not a malicious one: the file is not signed.
- A test checks that the entry point is callable and that the man page mentions every long option the parser has, so the two cannot drift apart silently.

## Exit codes

| Code | When |
| --- | --- |
| 0 | done |
| 1 | invalid vector, or the chart could not be written (the score is still printed first) |
| 2 | usage error, or an unusable `-o` path |

## Build order (one commit per step)

1. failing tests for the 3 reference vectors
2. metric tables and validation
3. `Roundup`, subscores and base score
4. severity
5. vector parse and build
6. CLI (interactive, then `--vector`)
7. `argparse` command line: `-v`, `-c`, `-o`, with the early `-o` path check
8. `build_svg`: title, bars, heights, colors, labels, negative impact as 0
9. `write_chart`: given path, temp folder by default, write errors
10. wiring: `save_chart` and `finish_run`, flags passed from `main`, end-to-end tests
11. the command line moves into the package (`cvss/app.py`), `main.py` becomes a shim
12. installable: `pyproject.toml` console script `cvss`, then the man page

The test list for each step comes from the domain sections, see `tests/cvss/test_core.py`, and the chart and CLI tests next to it.
