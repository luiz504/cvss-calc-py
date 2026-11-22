from dataclasses import dataclass

from cvss.formula import FORMULA


@dataclass(frozen=True)
class ChartColors:
    low: str = "#2ecc40"
    medium: str = "#1f4e9c"
    high: str = "#e67e22"
    critical: str = "#c0392b"


COLORS = ChartColors()


def color_for_score(score: float) -> str:
    if score >= FORMULA.high_min:
        return COLORS.high

    if score >= FORMULA.medium_min:
        return COLORS.medium

    return COLORS.low
