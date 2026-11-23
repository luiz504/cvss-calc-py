# Roadmap

What comes after `1.1.1`. Tick a box when the work is done and merged. The proposed version numbers are minor bumps
(each one adds a feature); the order can change, the **domain-first** order inside each version should not.

Every version below follows the same path, taken from how the base score was built:

1. **Domain first.** Extend [domain.md](domain.md) with the new definitions, values, formulas and reference vectors, taken
   from the [CVSS v3.1 specification](https://www.first.org/cvss/v3.1/specification-document) and checked against the
   [FIRST calculator](https://www.first.org/cvss/calculator/3.1) ([references.md](references.md)).
2. **Tests from the reference vectors**, red before the code (one test per rule).
3. **Constants and formula**, in `formula.py` and `core.py`, plain code with named numbers.
4. **Command line**: prompts and vector parsing.
5. **The chart**: the new panel and labels, real data only (no mocked values).
6. **Docs and release**: man page, README, `design.md`, changelog, version in `pyproject.toml` and in the man page
   header, then `make check`, both builds and the tag (see the note at the top of [../CHANGELOG.md](../CHANGELOG.md)).

## Domain check: where the project stands

| Concept (CVSS v3.1) | In `domain.md` | In the code | Planned in |
| --- | --- | --- | --- |
| Base metrics, base score, severity bands, vector string | yes | yes | done (`1.0`) |
| Temporal metric group and temporal score | no | no | `1.2.0` |
| Environmental metric group (security requirements, modified base metrics) and environmental score | no | no | `1.3.0` |
| Vector string with the temporal and environmental parts | base part only | base part only | `1.2.0`, `1.3.0` |
| "Overall" score (the highest level available, as the NVD shows it; a convention, not part of the specification) | no | no | `1.4.0` |
| Chart panels and labels for everything above | base scores only | base scores only | each version, finished in `1.4.0` |
| Translation (labels, messages, chart text) | no ("English only" in `design.md`) | no | `1.5.0` |

Two statements in the docs will stop being true and must be changed with the work that breaks them: *"Scope of this
project: the base score only"* (`domain.md`, `README.md`) and *"English only, no translations"* (`design.md`).

## 1.2.0 Temporal score

The temporal metrics (exploit code maturity, remediation level, report confidence) adjust the base score down; each has a
"Not Defined" value that changes nothing, so a vector without them keeps working exactly as today.

- [ ] `domain.md`: a "Temporal metrics" section with the three metrics, their values and weights, the formula, the vector
  suffix and reference vectors. Check every number against the specification (the section names are *Temporal Metric
  Group*, *Equations* and *Metric Values*).
- [ ] Reference vectors with their official temporal scores (the FIRST examples), cross-checked in the FIRST calculator.
- [ ] Definitions and weights in their own table next to `base_metrics.py`; optional metrics default to "Not Defined".
- [ ] `core.py`: the temporal score; `parse_vector` and `build_vector` accept and emit the temporal part only when it is
  there (base-only vectors stay identical).
- [ ] Command line: the interactive mode asks whether to add temporal metrics and then the three questions; the one-shot
  mode reads them from the vector; the result shows the temporal score and its severity.
- [ ] Chart: the Temporal panel and its row in the score list, colored by band.
- [ ] Docs and release (man page, README, `design.md`, `domain.md` scope line, changelog, version, tag).

## 1.3.0 Environmental score

The environmental metrics (the security requirements of the asset and the modified base metrics) adjust the score for one
organisation. The modified impact uses its own formula for a changed scope, different from the base one: copy it from the
specification, do not reuse the base code.

- [ ] `domain.md`: an "Environmental metrics" section: the requirement metrics, the modified base metrics (each also has
  "Not Defined", meaning "use the base value"), the modified subscores, the formula, the vector suffix, reference
  vectors.
- [ ] Reference vectors with official environmental scores, cross-checked in the FIRST calculator, including a changed
  scope and a case where the modified impact is zero or less.
- [ ] Definitions, weights and validation for the optional environmental metrics.
- [ ] `core.py`: the modified subscores and the environmental score (it also uses the temporal metrics); vector parse and
  build with the new part.
- [ ] Command line: an optional environmental block after the temporal one; one-shot through the vector.
- [ ] Chart: the Environmental panel (the environmental score and the modified impact) and its list row.
- [ ] Docs and release.

## 1.4.0 Overall score and the rest of the chart's labels

The chart today has one panel with three bars. The target is the full picture, built panel by panel in the versions above
and completed here: everything is real data, nothing mocked, and a metric group that was not given shows no bar and an
`NA` row.

- [ ] `domain.md`: the "overall" rule: the environmental score if any environmental metric is defined, else the temporal
  score if any temporal metric is defined, else the base score.
- [ ] `core.py`: the overall score and its severity.
- [ ] Chart, remaining labels and sections:
  - [ ] the Overall panel;
  - [ ] the score list (Base, Temporal, Environmental, Overall) with the value, the severity and `NA` where not defined;
  - [ ] the severity label on every bar and a small legend of the four bands;
  - [ ] the vector footer showing all the parts that were given;
  - [ ] a wider canvas and the new sizes as named constants in `ChartConstants`.
- [ ] Chart tests: one bar per value in each panel, the color of each band, the label texts, the `NA` rows, and the
  layout staying inside the canvas.
- [ ] Docs and release.

## 1.5.0 Translation

The program is English only today. Metrics and values already have stable keys (`ATTACK_VECTOR`, `NETWORK`), which the
CLI shows as they are. The first target language is Brazilian Portuguese (`pt-BR`); English stays the default.

Decisions to take before starting (my recommendation first):

- [ ] **How the language is chosen:** from the locale variables (`LC_ALL`, `LC_MESSAGES`, `LANG`) by default, with
  `--lang` as an override; or only one of them.
- [ ] **How the texts are stored:** a plain Python catalog per language (no dependency, works inside the standalone
  program) rather than `gettext` with `.po` files (an extra compile step at build time).
- [ ] **What is translated:** the prompts (groups, metric labels, value names), the severity words, the result labels, the
  messages and errors, `Generating chart...` and `Chart saved:`, the `-h` text, the chart texts, and the man page.
- [ ] **What is never translated:** the vector string and its letters, the option names, the exit codes, the file names.
- [ ] **The terms:** agree on the Portuguese words for the CVSS terms and record them in `domain.md`'s glossary as an
  English / Portuguese table (check whether a community glossary exists before inventing one).

Then the work:

- [ ] The catalog module and one lookup function; keys stay stable and English-based.
- [ ] A test that every key exists in every language, and that an unknown language falls back to English.
- [ ] The CLI texts, the chart texts and the `-h` text go through the lookup.
- [ ] Tests: the language is picked from the environment, `--lang` wins over it, colors are unaffected, no English left in
  a `pt-BR` run (spot checks on each kind of text).
- [ ] Packaging: the catalogs are in the wheel and inside the standalone program (check that PyInstaller picks them up).
- [ ] The Portuguese man page (installed under `man/pt_BR/man1`) and the README sections.
- [ ] Replace the *"English only"* decision in `design.md`, update the changelog, version, tag.

## Backlog (not tied to a version)

- [ ] `cvss --version` (and use it in the release smoke test).
- [ ] The installers leave a copy of their uninstaller in `~/.local/share/cvss/`, so uninstalling never needs the original
  file.
- [ ] An opt-in `--add-to-path` in the installers, and a better `PATH` note for bash and zsh.
- [ ] A `release.sh` and a tracked `pre-push` hook: no tag without the built installers.
- [ ] Decide whether to lower `requires-python` (the code needs 3.10+ syntax at least; today the floor is 3.12).
- [ ] More build targets for the standalone installer (for example `aarch64`).
