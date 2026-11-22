import sys
from pathlib import Path

from cvss.base_metrics import BASE_METRICS
from cvss.chart import write_chart
from cvss.colors import paint
from cvss.core import CvssError, build_vector, calculate_base_score, parse_vector, rate_severity

SEVERITY_STYLES = {"None": "dim", "Low": "green", "Medium": "yellow", "High": "red", "Critical": "critical"}


def print_result(metrics: dict[str, str]) -> None:
    score = calculate_base_score(metrics)
    severity = rate_severity(score)
    vector = build_vector(metrics)

    style = SEVERITY_STYLES[severity]

    print(f"{paint('Score:', 'bold')} {paint(str(score), style)}")
    print(f"{paint('Severity:', 'bold')} {paint(severity, style)}")
    print(f"{paint('Vector:', 'bold')} {vector}")


def save_chart(metrics: dict[str, str], output: Path | None) -> int:
    print(paint("Generating chart...", "dim"))

    try:
        path = write_chart(metrics, output)
    except OSError as error:
        print(f"{paint('cvss: error:', 'red')} cannot write the chart: {error}", file=sys.stderr)
        return 1

    print(f"{paint('Chart saved:', 'green')} {path}")
    return 0


def finish_run(metrics: dict[str, str], chart: bool, output: Path | None) -> int:
    print_result(metrics)

    if chart or output is not None:
        return save_chart(metrics, output)

    return 0


def run_interactive(chart: bool = False, output: Path | None = None) -> int:
    metrics = {}
    total_steps = len(BASE_METRICS)
    step = 0

    for metric in BASE_METRICS:
        step = step + 1
        definition = BASE_METRICS[metric]
        values = definition["values"]

        options = ""
        for letter in values:
            options = options + letter + "=" + values[letter] + " "

        prefix = paint(f"[{step}/{total_steps} {definition['group']}]", "dim")
        name = paint(metric, "bold")

        while True:
            answer = input(f"{prefix} {name} {definition['label']} ({options.strip()}): ").strip().upper()

            if answer in values:
                break

            print(paint(f'{metric} must be one of {", ".join(values)} (got "{answer}")', "red"))

        metrics[metric] = answer

    return finish_run(metrics, chart, output)


def run_vector(vector: str, chart: bool = False, output: Path | None = None) -> int:
    try:
        metrics = parse_vector(vector)
    except CvssError as error:
        print(paint(str(error), "red"))
        return 1

    return finish_run(metrics, chart, output)
