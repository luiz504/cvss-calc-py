import pytest

from cvss.chat import COLORS, color_for_score


@pytest.mark.parametrize(
    ("score", "color"),
    [
        (0.0, COLORS.low),
        (3.9, COLORS.low),
        (4.0, COLORS.medium),
        (6.9, COLORS.medium),
        (7.0, COLORS.high),
        (8.9, COLORS.high),
        (9.0, COLORS.critical),
        (10.0, COLORS.critical),
    ],
)
def test_color_for_score_follows_the_severity_bands(score: float, color: str) -> None:
    assert color_for_score(score) == color
