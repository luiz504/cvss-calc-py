import pytest

from cvss.core import CvssError, base_score, validate

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


@pytest.mark.parametrize(("metrics"), [[], {}, None, 42, "string", 3.14])
def test_validate_rejects_non_dict_metrics(metrics: object) -> None:
    with pytest.raises(Exception) as excinfo:
        validate(metrics)  # not a dict
    assert str(excinfo.value) == "Metrics must be a dictionary"


def test_validate_accepts_valid_metrics() -> None:
    validate(VALID_METRICS)  # passing without raising an exception


def test_validate_rejects_missing_metrics() -> None:
    with pytest.raises(CvssError) as excinfo:
        validate({"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H"})  # missing A
    assert str(excinfo.value) == "Missing metric: A"


def test_validate_rejects_unknown_metrics() -> None:
    with pytest.raises(CvssError) as excinfo:
        validate(
            {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H", "X": "Y"}
        )  # unknown metric X
    assert str(excinfo.value) == "Unknown metric: X"


def test_validate_rejects_non_string_value() -> None:
    # the web mode can receive a JSON array like ["N"]
    with pytest.raises(CvssError, match="AV must be a string"):
        validate({**VALID_METRICS, "AV": ["N"]})


@pytest.mark.parametrize(
    ("metric", "value"),
    [
        ("AV", "Z"),  # letter not allowed for this metric
        ("S", "N"),  # valid letter, but of another metric
        ("AV", "n"),  # lowercase is rejected
        ("AC", ""),  # empty string
    ],
)
def test_validate_rejects_invalid_value(metric: str, value: str) -> None:
    with pytest.raises(CvssError, match=f"{metric} must be one of"):
        validate({**VALID_METRICS, metric: value})
