import pytest

import main as entry


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    called = []
    monkeypatch.setattr(entry, "run", lambda: called.append("run"))
    monkeypatch.setattr(entry, "serve", lambda: called.append("serve"))
    return called


def test_main_without_command_prints_usage(calls: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = entry.main(["main.py"])

    assert exit_code == 2
    assert "Usage: python main.py cli|web" in capsys.readouterr().out
    assert calls == []


@pytest.mark.parametrize("command", ["nope", "CLI", "--vector"])
def test_main_rejects_unknown_command(calls: list[str], command: str) -> None:
    assert entry.main(["main.py", command]) == 2
    assert calls == []


@pytest.mark.parametrize("command", ["cli", "web"])
def test_main_rejects_extra_arguments(calls: list[str], command: str) -> None:
    assert entry.main(["main.py", command, "extra"]) == 2
    assert calls == []
