import xml.etree.ElementTree as ET

import pytest

from cvss.chat import COLORS, build_svg, color_for_score
from cvss.core import CvssError, build_vector, parse_vector

SVG_NS = "{http://www.w3.org/2000/svg}"

CRITICAL = parse_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")


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


def find_all(svg: str, css_class: str) -> list[ET.Element]:
    root = ET.fromstring(svg)
    found = []

    for element in root.iter():
        if element.get("class") == css_class:
            found.append(element)

    return found


def test_build_svg_rejects_invalid_metrics() -> None:
    with pytest.raises(CvssError):
        build_svg({})


def test_build_svg_returns_an_svg_document() -> None:
    root = ET.fromstring(build_svg(CRITICAL))

    assert root.tag == SVG_NS + "svg"


def test_build_svg_has_the_title() -> None:
    titles = find_all(build_svg(CRITICAL), "title")

    assert [title.text for title in titles] == ["BaseScores"]


def test_build_svg_shows_the_vector() -> None:
    vectors = find_all(build_svg(CRITICAL), "vector")

    assert [vector.text for vector in vectors] == [build_vector(CRITICAL)]


def test_build_svg_draws_one_bar_per_base_value() -> None:
    assert len(find_all(build_svg(CRITICAL), "bar")) == 3
