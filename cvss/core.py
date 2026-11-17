from .base_weights import BASE_METRICS


class CvssError(Exception):
    pass


def validate(metrics: dict[str, str]) -> None:
    # 1. every metric must be valid
    for metric in BASE_METRICS:
        if metric not in metrics:
            raise CvssError(f"Missing metric: {metric}")

    # 2. every metric value must be valid
    for metric in metrics:
        if metric not in BASE_METRICS:
            raise CvssError(f"Unknown metric: {metric}")


def base_score(metrics: dict[str, str]) -> float:
    return 0.0
