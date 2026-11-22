import os
from pathlib import Path

import pytest

import main as entry

NEEDS_NON_ROOT = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    called: list[str] = []
    monkeypatch.setattr(entry, "run_interactive", lambda **_options: called.append("run_interactive") or 0)
    monkeypatch.setattr(entry, "run_vector", lambda vector, **_options: called.append(vector) or 0)
    return called


def test_main_without_flags_runs_the_interactive_mode(calls: list[str]) -> None:
    assert entry.main([]) == 0
    assert calls == ["run_interactive"]


@pytest.mark.parametrize("flag", ["-v", "--vector"])
def test_main_vector_flag_runs_the_one_shot_mode(calls: list[str], flag: str) -> None:
    assert entry.main([flag, "CVSS:3.1/AV:N"]) == 0
    assert calls == ["CVSS:3.1/AV:N"]


def test_main_returns_the_one_shot_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(entry, "run_vector", lambda vector, **_options: 1)

    assert entry.main(["-v", "bad"]) == 1


def test_main_returns_the_interactive_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(entry, "run_interactive", lambda **_options: 1)

    assert entry.main([]) == 1


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


def test_main_help_exits_with_usage(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        entry.main(["-h"])

    assert stop.value.code == 0
    assert "usage: cvss" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["-c", "--chart"])
def test_main_accepts_the_chart_flag(calls: list[str], flag: str) -> None:
    assert entry.main([flag]) == 0
    assert calls == ["run_interactive"]


@pytest.mark.parametrize("flag", ["-o", "--output"])
def test_main_accepts_an_output_path(calls: list[str], tmp_path: Path, flag: str) -> None:
    assert entry.main([flag, str(tmp_path / "score.svg")]) == 0
    assert calls == ["run_interactive"]


def test_main_overwrites_an_existing_output_file(calls: list[str], tmp_path: Path) -> None:
    target = tmp_path / "score.svg"
    target.write_text("old")

    assert entry.main(["-o", str(target)]) == 0
    assert calls == ["run_interactive"]


def test_main_accepts_a_bare_file_name_in_the_current_folder(
    calls: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert entry.main(["-o", "score.svg"]) == 0


def fail_with(argv: list[str], capsys: pytest.CaptureFixture[str]) -> str:
    with pytest.raises(SystemExit) as stop:
        entry.main(argv)

    assert stop.value.code == 2
    return capsys.readouterr().err


def test_main_rejects_output_in_a_missing_folder(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    message = fail_with(["-o", str(tmp_path / "nope" / "score.svg")], capsys)

    assert "does not exist" in message
    assert calls == []


def test_main_rejects_output_that_is_a_directory(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    message = fail_with(["-o", str(tmp_path)], capsys)

    assert "is a directory" in message
    assert calls == []


def test_main_rejects_output_inside_a_file(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    blocker = tmp_path / "file.txt"
    blocker.write_text("x")

    message = fail_with(["-o", str(blocker / "score.svg")], capsys)

    assert "not a directory" in message
    assert calls == []


def test_main_checks_the_output_before_the_one_shot_mode(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fail_with(["-v", "CVSS:3.1/AV:N", "-o", str(tmp_path / "nope" / "score.svg")], capsys)

    assert calls == []


@NEEDS_NON_ROOT
def test_main_rejects_output_in_a_read_only_folder(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder = tmp_path / "locked"
    folder.mkdir()
    folder.chmod(0o500)

    try:
        message = fail_with(["-o", str(folder / "score.svg")], capsys)
    finally:
        folder.chmod(0o700)

    assert "permission denied" in message
    assert calls == []


@NEEDS_NON_ROOT
def test_main_rejects_overwriting_a_read_only_file(
    calls: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "score.svg"
    target.write_text("old")
    target.chmod(0o400)

    message = fail_with(["-o", str(target)], capsys)

    assert "permission denied" in message
    assert calls == []


@pytest.fixture
def mode_args(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, bool, Path | None]]:
    recorded: list[tuple[str, bool, Path | None]] = []

    def fake_interactive(chart: bool = False, output: Path | None = None) -> int:
        recorded.append(("interactive", chart, output))
        return 0

    def fake_vector(vector: str, chart: bool = False, output: Path | None = None) -> int:
        recorded.append((vector, chart, output))
        return 0

    monkeypatch.setattr(entry, "run_interactive", fake_interactive)
    monkeypatch.setattr(entry, "run_vector", fake_vector)
    return recorded


def test_main_passes_no_chart_by_default(mode_args: list[tuple[str, bool, Path | None]]) -> None:
    entry.main([])

    assert mode_args == [("interactive", False, None)]


def test_main_passes_the_chart_flag_to_the_interactive_mode(mode_args: list[tuple[str, bool, Path | None]]) -> None:
    entry.main(["-c"])

    assert mode_args == [("interactive", True, None)]


def test_main_passes_the_output_path_to_the_interactive_mode(
    mode_args: list[tuple[str, bool, Path | None]], tmp_path: Path
) -> None:
    entry.main(["-o", str(tmp_path / "score.svg")])

    assert mode_args == [("interactive", False, tmp_path / "score.svg")]


def test_main_passes_the_chart_flag_to_the_one_shot_mode(mode_args: list[tuple[str, bool, Path | None]]) -> None:
    entry.main(["-v", "CVSS:3.1/AV:N", "-c"])

    assert mode_args == [("CVSS:3.1/AV:N", True, None)]
