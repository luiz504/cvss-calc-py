from typing import TypedDict


class MetricDefinition(TypedDict):
    label: str
    values: dict[str, str]


BASE_METRICS: dict[str, MetricDefinition] = {
    "AV": {
        "label": "ATTACK_VECTOR",
        "values": {
            "N": "NETWORK",
            "A": "ADJACENT",
            "L": "LOCAL",
            "P": "PHYSICAL",
        },
    },
    "AC": {
        "label": "ATTACK_COMPLEXITY",
        "values": {
            "L": "LOW",
            "H": "HIGH",
        },
    },
    "PR": {
        "label": "PRIVILEGES_REQUIRED",
        "values": {
            "N": "NONE",
            "L": "LOW",
            "H": "HIGH",
        },
    },
    "UI": {
        "label": "USER_INTERACTION",
        "values": {
            "N": "NONE",
            "R": "REQUIRED",
        },
    },
    "S": {
        "label": "SCOPE",
        "values": {
            "U": "UNCHANGED",
            "C": "CHANGED",
        },
    },
    "C": {
        "label": "CONFIDENTIALITY",
        "values": {
            "H": "HIGH",
            "L": "LOW",
            "N": "NONE",
        },
    },
    "I": {
        "label": "INTEGRITY",
        "values": {
            "H": "HIGH",
            "L": "LOW",
            "N": "NONE",
        },
    },
    "A": {
        "label": "AVAILABILITY",
        "values": {
            "H": "HIGH",
            "L": "LOW",
            "N": "NONE",
        },
    },
}


# S (Scope) has no weight of its own. It only changes the PR weight and the impact formula.
BASE_METRICS_WEIGHTS: dict[str, dict[str, float]] = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "PR": {"N": 0.85, "L": 0.62, "H": 0.27},  # when scope is Unchanged
    "UI": {"N": 0.85, "R": 0.62},
    "C": {"H": 0.56, "L": 0.22, "N": 0},
    "I": {"H": 0.56, "L": 0.22, "N": 0},
    "A": {"H": 0.56, "L": 0.22, "N": 0},
}

# PR is the only weight that depends on another metric: these apply when scope is Changed.
PR_WEIGHTS_SCOPE_CHANGED: dict[str, float] = {"N": 0.85, "L": 0.68, "H": 0.5}
