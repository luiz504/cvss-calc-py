import pytest

from cvss import colors


@pytest.mark.usefixtures("colored")
def test_paint_wraps_the_text_in_the_style_and_a_reset() -> None:
    assert colors.paint("hi", "red") == "\033[31mhi\033[0m"


@pytest.mark.usefixtures("colored")
def test_colors_are_on_without_any_terminal_or_flag() -> None:
    assert colors.enabled() is True


def test_no_color_turns_them_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")

    assert colors.paint("hi", "green") == "hi"


@pytest.mark.usefixtures("colored")
def test_an_empty_no_color_does_not_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "")

    assert colors.paint("hi", "green") == "\033[32mhi\033[0m"


@pytest.mark.usefixtures("colored")
def test_a_dumb_terminal_turns_them_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TERM", "dumb")

    assert colors.paint("hi", "green") == "hi"
