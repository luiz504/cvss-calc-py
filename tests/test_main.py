import pytest

import main as entry


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    called = []
    monkeypatch.setattr(entry, "run_interactive", lambda: called.append("run_interactive"))
    monkeypatch.setattr(entry, "run_vector", lambda vector: called.append(vector) or 0)
    return called


def test_main_without_flags_runs_the_interactive_mode(calls: list[str]) -> None:
    assert entry.main([]) == 0
    assert calls == ["run_interactive"]


@pytest.mark.parametrize("flag", ["-v", "--vector"])
def test_main_vector_flag_runs_the_one_shot_mode(calls: list[str], flag: str) -> None:
    assert entry.main([flag, "CVSS:3.1/AV:N"]) == 0
    assert calls == ["CVSS:3.1/AV:N"]


def test_main_returns_the_one_shot_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(entry, "run_vector", lambda vector: 1)

    assert entry.main(["-v", "bad"]) == 1


@pytest.mark.parametrize("argv", [["-v"], ["--vector"]])
def test_main_rejects_flag_without_value(calls: list[str], argv: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        entry.main(argv)

    assert stop.value.code == 2
    assert calls == []


@pytest.mark.parametrize("argv", [["cli"], ["--nope"], ["extra"], ["--vec", "CVSS:3.1/AV:N"]])
def test_main_rejects_unknown_arguments(calls: list[str], argv: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        entry.main(argv)

    assert stop.value.code == 2
    assert calls == []
