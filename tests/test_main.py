import pytest

import main as entry


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    called = []
    monkeypatch.setattr(entry, "run_vector", lambda: called.append("run_vector"))
    monkeypatch.setattr(entry, "run_vector", lambda vector: called.append(vector) or 0)
    return called


def test_main_without_command_prints_usage(calls: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = entry.main(["main.py"])

    assert exit_code == 2
    assert "Usage: python main.py cli" in capsys.readouterr().out
    assert calls == []


@pytest.mark.parametrize("command", ["nope", "CLI", "--vector", "web"])
def test_main_rejects_unknown_command(calls: list[str], command: str) -> None:
    assert entry.main(["main.py", command]) == 2
    assert calls == []


def test_main_rejects_extra_arguments(calls: list[str]) -> None:
    assert entry.main(["main.py", "cli", "extra"]) == 2
    assert calls == []


def test_main_cli_runs_the_interactive_mode(calls: list[str]) -> None:
    assert entry.main(["main.py", "cli"]) == 0
    assert calls == ["run_interactive"]


def test_main_rejects_vector_flag_without_value(calls: list[str]) -> None:
    assert entry.main(["main.py", "cli", "--vector"]) == 2
    assert calls == []


def test_main_cli_vector_runs_the_one_shot_mode(calls: list[str]) -> None:
    assert entry.main(["main.py", "cli", "--vector", "CVSS:3.1/AV:N"]) == 0
    assert calls == ["CVSS:3.1/AV:N"]
