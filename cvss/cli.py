from cvss.base_metrics import BASE_METRICS
from cvss.core import base_score


def run() -> None:
    metrics = {}

    for metric in BASE_METRICS:
        definition = BASE_METRICS[metric]
        values = definition["values"]

        options = ""
        for letter in values:
            options = options + letter + "=" + values[letter] + " "

        while True:
            answer = input(f"{metric} {definition['label']} ({options.strip()}): ").strip().upper()

            if answer in values:
                break

            print(f'{metric} must be one of {", ".join(values)} (got "{answer}")')

        metrics[metric] = answer

    score = base_score(metrics)

    print(f"Score: {score}")


if __name__ == "__main__":
    run()

# Todo: add a semantic prefix per question showing the step group, and the step number
