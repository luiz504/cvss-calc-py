from dataclasses import dataclass
from pathlib import Path

from .core import build_vector, calculate_base_score, calculate_subscores, validate_metrics
from .formula import FORMULA


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
    baseline_y: int = 250
    first_bar_x: int = 50
    bar_width: int = 80
    bar_gap: int = 30
    name_size: int = 13
    name_offset_y: int = 22
    plot_height: int = 200
    value_size: int = 13
    value_offset_y: int = 8


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

    score = calculate_base_score(metrics)
    exploitability, impact = calculate_subscores(metrics)

    if impact < 0:
        impact = 0.0

    values = [("Base", score), ("Impact", impact), ("Exploitability", exploitability)]
    lines = []
    lines.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{CHART.width}" height="{CHART.height}" font-family="sans-serif">'
    )
    lines.append(f'<rect width="{CHART.width}" height="{CHART.height}" fill="{COLORS.background}"/>')
    lines.append(
        f'<text class="title" x="{CHART.title_x}" y="{CHART.title_y}" font-size="{CHART.title_size}" '
        f'font-weight="bold" fill="{COLORS.text}" text-anchor="middle">BaseScores</text>'
    )
    index = 0

    for name, value in values:
        x = CHART.first_bar_x + index * (CHART.bar_width + CHART.bar_gap)
        center = x + CHART.bar_width // 2
        shown = round(value, 1)
        height = round(shown / FORMULA.max_score * CHART.plot_height)
        y = CHART.baseline_y - height
        color = color_for_score(shown)

        lines.append(f'<rect class="bar" x="{x}" y="{y}" width="{CHART.bar_width}" height="{height}" fill="{color}"/>')
        lines.append(
            f'<text class="value" x="{center}" y="{y - CHART.value_offset_y}" '
            f'font-size="{CHART.value_size}" fill="{COLORS.text}" text-anchor="middle">{shown:.1f}</text>'
        )
        lines.append(
            f'<text class="name" x="{center}" y="{CHART.baseline_y + CHART.name_offset_y}" '
            f'font-size="{CHART.name_size}" fill="{COLORS.text}" text-anchor="middle">{name}</text>'
        )
        index = index + 1

    lines.append(
        f'<text class="vector" x="{CHART.vector_x}" y="{CHART.vector_y}" font-size="{CHART.vector_size}" '
        f'fill="{COLORS.text}" text-anchor="middle">{build_vector(metrics)}</text>'
    )
    lines.append("</svg>")

    return "\n".join(lines)


def write_chart(metrics: dict[str, str], path: Path) -> Path:
    svg = build_svg(metrics)
    path.write_text(svg, encoding="utf-8")

    return path
