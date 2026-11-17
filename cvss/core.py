from .base_weights import BASE_METRICS


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


def base_score(metrics: dict[str, str]) -> float:
    return 0.0
