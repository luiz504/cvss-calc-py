# Design

Decisions for how the code is organised. The rules being implemented are in [domain.md](domain.md).

## Decisions

- Base score only (CVSS 3.1). No temporal or environmental scores.
- Metrics are plain `dict[str, str]` (e.g. `{"AV": "N", "AC": "L", ...}`), not a class. They serialize to JSON for free.
- `Roundup` follows the specification's integer version, not `ceil(x * 10) / 10`.
- English only, no translations in v1. Metrics and values are stored under stable uppercase keys (e.g. `ATTACK_VECTOR`, `NETWORK`), which the CLI and the web UI show as they are.
- Definitions and weights are separate tables: `BASE_METRICS` says which metrics and letters exist, `BASE_METRICS_WEIGHTS` holds the scoring numbers.
- The CLI and the web UI contain **no scoring rules**. Both call `core`, so they always agree.

## `cvss/core.py` (pure: no I/O, no printing)

```text
BASE_METRICS                             # per metric: a label key and its allowed values {letter: key}
BASE_METRICS_WEIGHTS                    # weights for the formula
PR_WEIGHTS_SCOPE_CHANGED                 # PR weights when the scope is changed
FORMULA                                  # frozen dataclass from formula.py: formula numbers, severity limits
validate(metrics) -> None                # raises CvssError
subscores(metrics) -> (exploitability, impact)   # unrounded
base_score(metrics) -> float             # validates, then computes (one decimal)
severity(score) -> str                   # None | Low | Medium | High | Critical
parse_vector(vector) -> dict[str, str]   # optional, cut first if short on time
build_vector(metrics) -> str             # "CVSS:3.1/AV:N/..."
```

- One error type: `CvssError(ValueError)`. Messages name the metric and the allowed values, e.g. `AV must be one of N, A, L, P (got "X")`. The CLI prints the message and the web returns it in a 400, so the wording lives in one place.
- The CLI prompts and the web form options are both generated from `BASE_METRICS`.

## Modules

| Module | Responsibility |
| --- | --- |
| `formula.py` | named constants: formula numbers, severity limits, vector prefix |
| `base_metrics.py` | metric definitions and weights |
| `core.py` | scoring rules, validation, severity, vector build |
| `cli.py` | prompts, `--vector` flag, printing; loops on `CvssError` until the input is valid |
| `web.py` | `http.server` handler, JSON in/out, turns `CvssError` into HTTP 400 |
| `static/index.html` | the form; builds itself from `GET /api/metrics` |
| `main.py` | entry point: `cli` or `web` |

## Web contract (`127.0.0.1` only)

```text
GET  /              -> static/index.html
GET  /api/metrics   -> metrics, allowed values and labels
POST /api/score
  request:  {"metrics": {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}}
  200:      {"score": 9.8, "severity": "Critical", "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}
  400:      {"error": "AV must be one of N, A, L, P (got \"X\")"}
```

Anything else returns 404. Request bodies are capped at about 1 KB.

## Build order (one commit per step)

1. failing tests for the 3 reference vectors
2. metric tables and validation
3. `Roundup`, subscores and base score
4. severity
5. vector parse and build
6. CLI, then the web server and page

The test list for each step comes from the domain sections, see `tests/test_core.py`.
