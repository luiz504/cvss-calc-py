from dataclasses import dataclass

from cvss.core import validate_metrics
from cvss.formula import FORMULA


@dataclass(frozen=True)
class ChartColors:
    low: str = "#2ecc40"
    medium: str = "#1f4e9c"
    high: str = "#e67e22"
    critical: str = "#c0392b"

    text: str = "#333333"
    background: str = "#ffffff"


COLORS = ChartColors()


@dataclass(frozen=True)
class ChartConstants:
    width: int = 400
    height: int = 320
    title_x: int = 200
    title_y: int = 32
    title_size: int = 18
    vector_x: int = 200
    vector_y: int = 296
    vector_size: int = 11


CHART = ChartConstants()


def color_for_score(score: float) -> str:
    if score >= FORMULA.critical_min:
        return COLORS.critical

    if score >= FORMULA.high_min:
        return COLORS.high

    if score >= FORMULA.medium_min:
        return COLORS.medium

    return COLORS.low


def build_svg(metrics: dict[str, str]) -> str:
    validate_metrics(metrics)

    lines = []
    lines.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{CHART.width}" height="{CHART.height}" font-family="sans-serif">'
    )
    lines.append(
        f'<text class="title" x="{CHART.title_x}" y="{CHART.title_y}" font-size="{CHART.title_size}" '
        f'font-weight="bold" fill="{COLORS.text}" text-anchor="middle">BaseScores</text>'
    )
    lines.append("</svg>")

    return "\n".join(lines)
