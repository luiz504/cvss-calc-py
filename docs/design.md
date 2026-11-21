# Design

Decisions for how the code is organised. The rules being implemented are in [domain.md](domain.md).

## Decisions

- Base score only (CVSS 3.1). No temporal or environmental scores.
- Metrics are plain `dict[str, str]` (e.g. `{"AV": "N", "AC": "L", ...}`), not a class. They serialize to JSON for free.
- `Roundup` follows the specification's integer version, not `ceil(x * 10) / 10`.
- English only, no translations in v1. Metrics and values are stored under stable uppercase keys (e.g. `ATTACK_VECTOR`, `NETWORK`), which the CLI shows as they are.
- Definitions and weights are separate tables: `BASE_METRICS` says which metrics and letters exist, `BASE_METRICS_WEIGHTS` holds the scoring numbers.
- The CLI contains **no scoring rules**. It calls `core`.

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

## Modules

| Module | Responsibility |
| --- | --- |
| `formula.py` | named constants: formula numbers, severity limits, vector prefix |
| `base_metrics.py` | metric definitions and weights |
| `core.py` | scoring rules, validation, severity, vector build |
| `cli.py` | prompts, loops until each answer is valid, printing; `--vector` flag _(planned)_ |
| `main.py` | entry point: `cli` |

## Build order (one commit per step)

1. failing tests for the 3 reference vectors
2. metric tables and validation
3. `Roundup`, subscores and base score
4. severity
5. vector parse and build
6. CLI (interactive, then `--vector`)

The test list for each step comes from the domain sections, see `tests/cvss/test_core.py`.
