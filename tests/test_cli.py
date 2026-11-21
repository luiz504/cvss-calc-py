import pytest

from cvss.cli import run

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

    run()

    output = capsys.readouterr().out

    assert 'AV must be one of N, A, L, P (got "X")' in output
    assert 'AV must be one of N, A, L, P (got "Z")' in output

    asked = []
    for prompt in prompts:
        asked.append(prompt.split(" ")[0])
    assert asked == ["AV", "AV", "AV", "AC", "PR", "UI", "S", "C", "I", "A"]


def test_cli_prints_score(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run()

    assert "Score: 9.8" in capsys.readouterr().out


def test_cli_prints_severity(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run()

    assert "Severity: Critical" in capsys.readouterr().out


def test_cli_prints_vector(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, VALID_ANSWERS)

    run()

    assert "Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" in capsys.readouterr().out


def test_cli_prompt_lists_the_options(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run()

    assert prompts[0] == "AV ATTACK_VECTOR (N=NETWORK A=ADJACENT L=LOCAL P=PHYSICAL): "


def test_cli_accepts_lowercase_and_spaces(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, [" n", "l ", "n", "n", "u", "h", "h", " h "])

    run()

    assert "Score: 9.8" in capsys.readouterr().out


def test_cli_asks_each_metric_once_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run()

    asked = []
    for prompt in prompts:
        asked.append(prompt.split(" ")[0])

    assert asked == ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
    prompts = fake_input(monkeypatch, VALID_ANSWERS)

    run()

    asked = []

    for prompt in prompts:
        asked.append(prompt.split(" ")[0])

    assert asked == ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
