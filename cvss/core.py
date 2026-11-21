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

    scope_changed = metrics["S"] == "C"

    if scope_changed:
        pr_weight = PR_WEIGHTS_SCOPE_CHANGED[metrics["PR"]]
    else:
        pr_weight = BASE_METRICS_WEIGHTS["PR"][metrics["PR"]]

    ui_weight = BASE_METRICS_WEIGHTS["UI"][metrics["UI"]]

    exploitability = FORMULA.exploitability_coefficient * av_weight * ac_weight * pr_weight * ui_weight

    c_weight = BASE_METRICS_WEIGHTS["C"][metrics["C"]]
    i_weight = BASE_METRICS_WEIGHTS["I"][metrics["I"]]
    a_weight = BASE_METRICS_WEIGHTS["A"][metrics["A"]]

    # Base metrics equation: 7.1 of CVSS v3.1 Specification
    iss = 1 - ((1 - c_weight) * (1 - i_weight) * (1 - a_weight))

    if scope_changed:
        coefficient = FORMULA.impact_coefficient_changed * (iss - FORMULA.impact_changed_offset)
        penalty = FORMULA.impact_penalty_coefficient * (
            (iss - FORMULA.impact_penalty_offset) ** FORMULA.impact_penalty_exponent
        )
        impact = coefficient - penalty

    else:
        impact = FORMULA.impact_coefficient_unchanged * iss

    return exploitability, impact


def base_score(metrics: dict[str, str]) -> float:
    validate(metrics)

    exploitability, impact = subscores(metrics)

    # No impact at all: the score is 0, whatever the exploitability is.
    # subscores returns the raw value, so impact can be negative (scope changed, C/I/A all None: about -0.218).
    if impact <= 0:
        return 0.0

    total = exploitability + impact

    scope_changed = metrics["S"] == "C"

    if scope_changed:
        total = total * FORMULA.scope_changed_multiplier

    return roundup(min(total, FORMULA.max_score))


def severity(score: float) -> str:
    if isinstance(score, bool) or not isinstance(score, int | float):
        raise CvssError("Score must be a number")

    if score < FORMULA.min_score or score > FORMULA.max_score:
        raise CvssError(f"Score must be between {FORMULA.min_score} and {FORMULA.max_score} (got {score})")

    if score >= FORMULA.critical_min:
        return "Critical"

    if score >= FORMULA.high_min:
        return "High"

    if score >= FORMULA.medium_min:
        return "Medium"

    if score >= FORMULA.low_min:
        return "Low"

    return "None"


def build_vector(metrics: dict[str, str]) -> str:
    validate(metrics)

    vector = FORMULA.vector_prefix

    for metric in BASE_METRICS:
        vector = vector + "/" + metric + ":" + metrics[metric]

    return vector
