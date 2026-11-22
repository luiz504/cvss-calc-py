import pytest


@pytest.fixture(autouse=True)
def plain_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts with NO_COLOR set, so output assertions see plain text. Color tests use `colored`."""
    monkeypatch.setenv("NO_COLOR", "1")


@pytest.fixture
def colored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("TERM", raising=False)
