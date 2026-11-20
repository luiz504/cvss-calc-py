from .base_metrics import BASE_METRICS, BASE_METRICS_WEIGHTS, PR_WEIGHTS_SCOPE_CHANGED
from .formula import FORMULA


class CvssError(ValueError):
    pass


def validate(metrics: dict[str, str]) -> None:
    # 0. the input itself must be a dict (it can come from JSON or the CLI)
    if not isinstance(metrics, dict):
        raise CvssError("Metrics must be a dictionary")

    # 1. every metric must be present
    for metric in BASE_METRICS:
        if metric not in metrics:
            raise CvssError(f"Missing metric: {metric}")

    # 2. no unknown metrics
    for metric in metrics:
        if metric not in BASE_METRICS:
            raise CvssError(f"Unknown metric: {metric}")

    # 3. every metric value must be a string and one of the allowed letters
    for metric in BASE_METRICS:
        allowed = BASE_METRICS[metric]["values"]
        value = metrics[metric]

        if not isinstance(value, str):
            raise CvssError(f"{metric} must be a string")

        if value not in allowed:
            raise CvssError(f'{metric} must be one of {", ".join(allowed)} (got "{value}")')


def roundup(value: float) -> float:
    int_input = round(value * 100000)

    if int_input % 10000 == 0:
        return int_input / 100000

    return (int_input // 10000 + 1) / 10


def subscores(metrics: dict[str, str]) -> tuple[float, float]:
    av_weight = BASE_METRICS_WEIGHTS["AV"][metrics["AV"]]
    ac_weight = BASE_METRICS_WEIGHTS["AC"][metrics["AC"]]

    print(f"😈😈😈 DEBUG: scope {metrics['S']}")
    scope_changed = metrics["S"] == "C"

    if scope_changed:
        pr_weight = PR_WEIGHTS_SCOPE_CHANGED[metrics["PR"]]
    else:
        pr_weight = BASE_METRICS_WEIGHTS["PR"][metrics["PR"]]

    ui_weight = BASE_METRICS_WEIGHTS["UI"][metrics["UI"]]

    exploitability = FORMULA.exploitability_coefficient * av_weight * ac_weight * pr_weight * ui_weight

    return exploitability, 0.0  # impact is not implemented yet


def base_score(metrics: dict[str, str]) -> float:
    return 0.0
