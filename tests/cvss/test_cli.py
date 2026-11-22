from pathlib import Path

import pytest

from cvss.cli import run_interactive, run_vector, save_chart
from cvss.core import parse_vector

VALID_ANSWERS = ["N", "L", "N", "N", "U", "H", "H", "H"]  # AV AC PR UI S C I A -> 9.8 Critical


def fake_input(monkeypatch: pytest.MonkeyPatch, answers: list[str]) -> list[str]:
    """Replace input() by a fake that hands out the answers one by one. Returns the prompts it was asked."""
    prompts = []
    answer_iterator = iter(answers)

    def fake(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answer_iterator)

    monkeypatch.setattr("builtins.input", fake)
    return prompts


def test_cli_asks_again_until_the_answer_is_valid(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    prompts = fake_input(monkeypatch, ["X", "Z", *VALID_ANSWERS])

    run_interactive()

    output = capsys.readouterr().out

    assert 'AV must be one of N, A, L, P (got "X")' in output
    assert 'AV must be one of N, A, L, P (got "Z")' in output

    # AV is asked three times (X, Z, N) and keeps its step: the same question comes back until it is valid
    expected_starts = [
        "[1/8 EXPLOITABILITY] AV ",
        "[1/8 EXPLOITABILITY] AV ",
        "[1/8 EXPLOITABILITY] AV ",
        "[2/8 EXPLOITABILITY] AC ",
        "[3/8 EXPLOITABILITY] PR ",
        "[4/8 EXPLOITABILITY] UI ",
        "[5/8 SCOPE] S ",
        "[6/8 IMPACT] C ",
        "[7/8 IMPACT] I ",
        "[8/8 IMPACT] A ",
    ]

    assert len(prompts) == len(expected_starts)

    for index, expected_start in enumerate(expected_starts):
        assert prompts[index].startswith(expected_start)


def test_cli_prints_score(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    assert "Score: 9.8" in capsys.readouterr().out


def test_cli_prints_severity(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    assert "Severity: Critical" in capsys.readouterr().out


def test_cli_prints_vector(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    assert "Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" in capsys.readouterr().out


def test_cli_prompt_lists_the_options(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    assert prompts[0] == "[1/8 EXPLOITABILITY] AV ATTACK_VECTOR (N=NETWORK A=ADJACENT L=LOCAL P=PHYSICAL): "


def test_cli_accepts_lowercase_and_spaces(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, [" n", "l ", "n", "n", "u", "h", "h", " h "])

    run_interactive()

    assert "Score: 9.8" in capsys.readouterr().out


def test_cli_prompts_show_step_and_group_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    asked = []
    for prompt in prompts:
        asked.append(prompt.split(" ")[0])

    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run_interactive()

    expected_starts = [
        "[1/8 EXPLOITABILITY] AV ",
        "[2/8 EXPLOITABILITY] AC ",
        "[3/8 EXPLOITABILITY] PR ",
        "[4/8 EXPLOITABILITY] UI ",
        "[5/8 SCOPE] S ",
        "[6/8 IMPACT] C ",
        "[7/8 IMPACT] I ",
        "[8/8 IMPACT] A ",
    ]

    assert len(prompts) == len(expected_starts)
    for index, expected_start in enumerate(expected_starts):
        assert prompts[index].startswith(expected_start)


def test_cli_interactive_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    assert run_interactive() == 0


# --- run-vector ---


def test_cli_vector_prints_the_error_for_an_invalid_vector(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_vector("nope")

    assert exit_code == 1
    assert 'Vector must start with "CVSS:3.1/"' in capsys.readouterr().out


def test_cli_vector_prints_the_result(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Score: 9.8" in output
    assert "Severity: Critical" in output
    assert "Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" in output


# --- save-chart ---
CRITICAL_VECTOR = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
CRITICAL = parse_vector(CRITICAL_VECTOR)
ChartCall = tuple[dict[str, str], Path | None]


@pytest.fixture
def chart_calls(monkeypatch: pytest.MonkeyPatch) -> list[ChartCall]:
    calls: list[ChartCall] = []

    def fake_write_chart(metrics: dict[str, str], path: Path | None = None) -> Path:
        calls.append((metrics, path))
        return path if path is not None else Path("/fake/default.svg")

    monkeypatch.setattr("cvss.cli.write_chart", fake_write_chart)
    return calls


@pytest.fixture
def failing_chart(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_write_chart(metrics: dict[str, str], path: Path | None = None) -> Path:
        raise PermissionError("denied")

    monkeypatch.setattr("cvss.cli.write_chart", fake_write_chart)


@pytest.mark.usefixtures("chart_calls")
def test_save_chart_reports_the_saved_path(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = save_chart(CRITICAL, None)

    assert exit_code == 0
    assert capsys.readouterr().out == "Chart saved: /fake/default.svg\n"


def test_save_chart_passes_the_metrics_and_output_on(chart_calls: list[ChartCall]) -> None:
    save_chart(CRITICAL, Path("out.svg"))

    assert chart_calls == [(CRITICAL, Path("out.svg"))]
