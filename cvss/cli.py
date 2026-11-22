from cvss.base_metrics import BASE_METRICS
from cvss.core import CvssError, build_vector, calculate_base_score, parse_vector, rate_severity


def print_result(metrics: dict[str, str]) -> None:
    score = calculate_base_score(metrics)
    severity = rate_severity(score)
    vector = build_vector(metrics)

    print(f"Score: {score}")
    print(f"Severity: {severity}")
    print(f"Vector: {vector}")


def run_interactive() -> int:
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

        prefix = f"[{step}/{total_steps} {definition['group']}]"

        while True:
            answer = input(f"{prefix} {metric} {definition['label']} ({options.strip()}): ").strip().upper()

            if answer in values:
                break

            print(f'{metric} must be one of {", ".join(values)} (got "{answer}")')

        metrics[metric] = answer

    print_result(metrics)

    return 0


def run_vector(vector: str) -> int:
    try:
        metrics = parse_vector(vector)
    except CvssError as error:
        print(error)
        return 1
    print_result(metrics)
    return 0
