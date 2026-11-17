import pytest

from cvss.core import base_score


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
