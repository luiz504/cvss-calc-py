# Domain: CVSS v3.1 base score

What the calculator computes, and the rules it must follow. Source of truth: the [FIRST CVSS v3.1 specification](https://www.first.org/cvss/v3.1/specification-document). If this page and the specification disagree, the specification wins.

Scope of this project: the **base score** only. Temporal and environmental scores are out of scope.

## What CVSS is

The Common Vulnerability Scoring System rates how severe a vulnerability is on a scale of 0.0 to 10.0. The base score describes the vulnerability itself (how it is attacked and what it can damage), independent of any particular organisation or time.

## Base metrics

Eight metrics, each with a fixed set of allowed values.

| Metric | Name | Values (letter: meaning, weight) |
| --- | --- | --- |
| `AV` | Attack Vector | `N` Network 0.85, `A` Adjacent 0.62, `L` Local 0.55, `P` Physical 0.20 |
| `AC` | Attack Complexity | `L` Low 0.77, `H` High 0.44 |
| `PR` | Privileges Required | `N` None 0.85, `L` Low 0.62 (0.68 if scope changed), `H` High 0.27 (0.50 if scope changed) |
| `UI` | User Interaction | `N` None 0.85, `R` Required 0.62 |
| `S` | Scope | `U` Unchanged, `C` Changed (no weight of its own; it changes the formulas below) |
| `C` | Confidentiality Impact | `H` High 0.56, `L` Low 0.22, `N` None 0.00 |
| `I` | Integrity Impact | `H` High 0.56, `L` Low 0.22, `N` None 0.00 |
| `A` | Availability Impact | `H` High 0.56, `L` Low 0.22, `N` None 0.00 |

Input rules:

- All eight metrics are required, each exactly once.
- Only the listed letters are valid. Anything else is an error.
- `PR` is the only weight that depends on another metric (`S`).

## Formulas

Notation: `AV`, `AC`, `PR`, `UI`, `C`, `I`, `A` stand for the **weights** from the table above.

```text
ISS            = 1 - (1 - C) * (1 - I) * (1 - A)

Impact         = 6.42 * ISS                                     if S = U
               = 7.52 * (ISS - 0.029) - 3.25 * (ISS - 0.02)^15  if S = C

Exploitability = 8.22 * AV * AC * PR * UI

Base score     = 0                                              if Impact <= 0
               = Roundup( min(Impact + Exploitability, 10) )     if S = U
               = Roundup( min(1.08 * (Impact + Exploitability), 10) )  if S = C
```

`ISS` is the Impact Sub Score. `Impact` and `Exploitability` are the two subscores.

### Roundup

The score is rounded **up** to one decimal. The specification defines its own `Roundup` to avoid floating-point surprises (a naive `ceil(x * 10) / 10` can be off by 0.1):

```text
Roundup(x):
    int_input = round(x * 100000)
    if int_input mod 10000 = 0:
        return int_input / 100000
    else:
        return (floor(int_input / 10000) + 1) / 10
```

## Severity rating

| Score | Severity |
| --- | --- |
| 0.0 | None |
| 0.1 to 3.9 | Low |
| 4.0 to 6.9 | Medium |
| 7.0 to 8.9 | High |
| 9.0 to 10.0 | Critical |

## Vector string

A compact text form of the eight metrics, always in this order:

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

- Starts with the `CVSS:3.1` prefix.
- Followed by `metric:value` pairs separated by `/`.
- A missing, duplicated or unknown metric, or a wrong prefix, makes the vector invalid.

## Reference vectors

Used as the first tests. Cross-check them with the [FIRST calculator](https://www.first.org/cvss/calculator/3.1).

| Vector | Score | Severity |
| --- | --- | --- |
| `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | 9.8 | Critical |
| `AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N` | 6.1 | Medium |
| `AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` | 7.8 | High |

Worked example for the first vector: `ISS = 1 - 0.44^3 = 0.9148`, `Impact = 6.42 * 0.9148 = 5.873`, `Exploitability = 8.22 * 0.85 * 0.77 * 0.85 * 0.85 = 3.887`, and `Roundup(5.873 + 3.887) = Roundup(9.76) = 9.8`.

## Glossary

- **CVE**: an identifier for a publicly known vulnerability (e.g. `CVE-2021-44228`).
- **CVSS**: the scoring system described here, maintained by FIRST.
- **FIRST**: Forum of Incident Response and Security Teams, the organisation that publishes CVSS.
- **NVD**: the US National Vulnerability Database, which publishes CVSS scores for CVEs.
- **Base score**: the score from the eight base metrics, before any temporal or environmental adjustment.
