from cvss.base_metrics import BASE_METRICS
from cvss.core import build_vector, calculate_base_score, rate_severity


def run() -> None:
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

    score = calculate_base_score(metrics)
    severity = rate_severity(score)
    vector = build_vector(metrics)

    print(f"Score: {score}")
    print(f"Severity: {severity}")
    print(f"Vector: {vector}")
