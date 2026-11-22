from dataclasses import dataclass


@dataclass(frozen=True)
class ChartColors:
    low: str = "#2ecc40"
    medium: str = "#1f4e9c"
    high: str = "#e67e22"
    critical: str = "#c0392b"


COLORS = ChartColors()


def color_for_score(score: float) -> str:
    return COLORS.low
