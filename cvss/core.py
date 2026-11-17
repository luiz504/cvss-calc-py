from .base_weights import BASE_METRICS


class CvssError(Exception):
    pass


def validate(metrics: dict[str, str]) -> None:
    if not isinstance(metrics, dict):
        raise CvssError("Metrics must be a dictionary")

    #  every metric must be valid
    for metric in BASE_METRICS:
        if metric not in metrics:
            raise CvssError(f"Missing metric: {metric}")

    # every metric value must be valid
    for metric in metrics:
        if metric not in BASE_METRICS:
            raise CvssError(f"Unknown metric: {metric}")

    # 3. every metric value must be valid
    for metric in BASE_METRICS:
        allowed = BASE_METRICS[metric]
        value = metrics[metric]

        if not isinstance(value, str):
            raise CvssError(f"{metric} must be a string")


def base_score(metrics: dict[str, str]) -> float:
    return 0.0
