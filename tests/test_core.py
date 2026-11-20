import pytest

from cvss.core import CvssError, base_score, roundup, subscores, validate

VALID_METRICS = {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}


@pytest.mark.parametrize(
    ("metrics", "expected"),
    [
        ({"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}, 9.8),
        ({"AV": "N", "AC": "L", "PR": "N", "UI": "R", "S": "C", "C": "L", "I": "L", "A": "N"}, 6.1),
        ({"AV": "L", "AC": "L", "PR": "L", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}, 7.8),
    ],
    ids=["critical-network", "scope-changed-medium", "local-high"],
)
def test_base_score_matches_reference_vector(metrics: dict[str, str], expected: float) -> None:
    assert base_score(metrics) == expected


# --- validate ---


@pytest.mark.parametrize("metrics", [[], None, (), 42, "string", 3.14])
def test_validate_rejects_non_dict_metrics(metrics: object) -> None:
    with pytest.raises(CvssError) as excinfo:
        validate(metrics)  # type: ignore[arg-type]  # not a dict, on purpose
    assert str(excinfo.value) == "Metrics must be a dictionary"


def test_validate_accepts_valid_metrics() -> None:
    validate(VALID_METRICS)  # passing without raising an exception


@pytest.mark.parametrize(
    ("metrics", "expected_message"),
    [
        ({k: v for k, v in VALID_METRICS.items() if k != "A"}, "Missing metric: A"),
        ({}, "Missing metric: AV"),  # reports the first missing metric, in spec order
    ],
    ids=["one-missing", "all-missing"],
)
def test_validate_rejects_missing_metrics(metrics: dict[str, str], expected_message: str) -> None:
    with pytest.raises(CvssError) as excinfo:
        validate(metrics)
    assert str(excinfo.value) == expected_message


def test_validate_rejects_unknown_metrics() -> None:
    with pytest.raises(CvssError) as excinfo:
        validate(
            {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H", "X": "Y"}
        )  # unknown metric X
    assert str(excinfo.value) == "Unknown metric: X"


@pytest.mark.parametrize("value", [["N"], None, 1])
def test_validate_rejects_non_string_value(value: object) -> None:
    # the web mode can receive JSON values like ["N"], null or 1
    with pytest.raises(CvssError, match="AV must be a string"):
        validate({**VALID_METRICS, "AV": value})


@pytest.mark.parametrize(
    ("metric", "value"),
    [
        ("AV", "Z"),  # letter not allowed for this metric
        ("AV", "n"),  # lowercase is rejected
        ("AV", "NA"),  # two letters (would slip through a substring check)
        ("AC", ""),  # empty string
    ],
)
def test_validate_rejects_invalid_value(metric: str, value: str) -> None:
    with pytest.raises(CvssError, match=f"{metric} must be one of"):
        validate({**VALID_METRICS, metric: value})


# --- roundup ---
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 0.0),
        (4.0, 4.0),  # already exact
        (4.02, 4.1),  # just above: goes up
        (9.76, 9.8),
        (4.000000000000001, 4.0),  # float noise: a naive ceil(x * 10) / 10 would give 4.1
    ],
)
def test_roundup(value: float, expected: float) -> None:
    assert roundup(value) == expected


UNCHANGED = {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}
CHANGED = {"AV": "N", "AC": "L", "PR": "N", "UI": "R", "S": "C", "C": "L", "I": "L", "A": "N"}


# --- subscores ---
def test_exploitability_scope_unchanged() -> None:
    exploitability, _ = subscores(UNCHANGED)
    assert exploitability == pytest.approx(3.887, abs=0.001)


def test_exploitability_pr_low_scope_changed() -> None:
    # PR:L is 0.62 when unchanged but 0.68 when changed
    exploitability, _ = subscores({**UNCHANGED, "PR": "L", "S": "C"})
    assert exploitability == pytest.approx(3.110, abs=0.001)


def test_impact_scope_unchanged() -> None:
    _, impact = subscores(UNCHANGED)
    assert impact == pytest.approx(5.873, abs=0.001)


def test_impact_none_is_zero() -> None:
    _, impact = subscores({**UNCHANGED, "C": "N", "I": "N", "A": "N"})
    assert impact == 0


def test_impact_scope_changed() -> None:
    _, impact = subscores(CHANGED)
    assert impact == pytest.approx(2.727, abs=0.001)
