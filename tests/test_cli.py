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


def test_fake_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fake_input(monkeypatch, ["X", "Z", *VALID_ANSWERS])

    run()

    output = capsys.readouterr().out

    assert 'AV must be one of N, A, L, P (got "X")' in output
    assert 'AV must be one of N, A, L, P (got "Z")' in output


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
