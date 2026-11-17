BASE_METRICS: dict[str, dict[str, dict[str, str]]] = {
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
