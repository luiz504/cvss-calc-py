import pytest

from cvss.chat import COLORS, color_for_score


@pytest.mark.parametrize(
    ("score", "color"),
    [
        (0.0, COLORS.low),
        (3.9, COLORS.low),
    ],
)
def test_color_for_score_follows_the_severity_bands(score: float, color: str) -> None:
    assert color_for_score(score) == color
