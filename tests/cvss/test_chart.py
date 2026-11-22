import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cvss.chart import CHART, COLORS, build_svg, color_for_score, write_chart
from cvss.core import CvssError, build_vector, parse_vector

NEEDS_NON_ROOT = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
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


# --- build_svg ---


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


def test_build_svg_names_the_bars() -> None:
    names = find_all(build_svg(CRITICAL), "name")

    assert [name.text for name in names] == ["Base", "Impact", "Exploitability"]


def number(element: ET.Element, attribute: str) -> int:
    value = element.get(attribute)
    assert value is not None

    return int(value)


def test_build_svg_scales_bar_height_by_value() -> None:
    bars = find_all(build_svg(CRITICAL), "bar")

    # 9.8, 5.9 and 3.9 out of 10, on a 200 px plot
    assert [number(bar, "height") for bar in bars] == [196, 118, 78]


def test_build_svg_sits_every_bar_on_the_baseline() -> None:
    bars = find_all(build_svg(CRITICAL), "bar")

    for bar in bars:
        assert number(bar, "y") + number(bar, "height") == CHART.baseline_y


def test_build_svg_colors_bars_by_score_band() -> None:
    bars = find_all(build_svg(CRITICAL), "bar")

    assert [bar.get("fill") for bar in bars] == [COLORS.critical, COLORS.medium, COLORS.low]


def test_build_svg_colors_a_high_score_orange() -> None:
    high = parse_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L")  # base 7.3, impact 3.4, exploitability 3.9
    bars = find_all(build_svg(high), "bar")

    assert [bar.get("fill") for bar in bars] == [COLORS.high, COLORS.low, COLORS.low]


def test_build_svg_labels_bars_with_one_decimal() -> None:
    values = find_all(build_svg(CRITICAL), "value")

    assert [value.text for value in values] == ["9.8", "5.9", "3.9"]


def test_build_svg_shows_a_negative_impact_as_zero() -> None:
    no_impact = parse_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:N")  # base 0.0, raw impact below 0
    svg = build_svg(no_impact)

    values = find_all(svg, "value")
    bars = find_all(svg, "bar")

    assert [value.text for value in values] == ["0.0", "0.0", "3.9"]
    assert [number(bar, "height") for bar in bars] == [0, 0, 78]


# --- write chart ---
def test_write_chart_writes_the_svg_to_the_given_path(tmp_path: Path) -> None:
    target = tmp_path / "score.svg"

    result = write_chart(CRITICAL, target)

    assert result == target
    assert target.read_text(encoding="utf-8") == build_svg(CRITICAL)


def test_write_chart_overwrites_an_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "score.svg"
    target.write_text("old", encoding="utf-8")

    write_chart(CRITICAL, target)

    assert target.read_text(encoding="utf-8") == build_svg(CRITICAL)


def test_write_chart_writes_nothing_for_invalid_metrics(tmp_path: Path) -> None:
    target = tmp_path / "score.svg"

    with pytest.raises(CvssError):
        write_chart({}, target)

    assert not target.exists()


@pytest.fixture
def temp_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    return tmp_path


def test_write_chart_defaults_to_the_temp_folder(temp_folder: Path) -> None:
    result = write_chart(CRITICAL)

    assert result == temp_folder / "cvss-calc" / "cvss-score.svg"
    assert result.read_text(encoding="utf-8") == build_svg(CRITICAL)


def test_write_chart_default_overwrites_the_previous_run(temp_folder: Path) -> None:
    other = parse_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L")
    write_chart(CRITICAL)

    result = write_chart(other)

    assert result.read_text(encoding="utf-8") == build_svg(other)


def test_write_chart_raises_when_the_folder_is_missing(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        write_chart(CRITICAL, tmp_path / "nope" / "score.svg")


@NEEDS_NON_ROOT
def test_write_chart_raises_when_the_folder_is_read_only(tmp_path: Path) -> None:
    folder = tmp_path / "locked"
    folder.mkdir()
    folder.chmod(0o500)

    try:
        with pytest.raises(PermissionError):
            write_chart(CRITICAL, folder / "score.svg")
    finally:
        folder.chmod(0o700)
