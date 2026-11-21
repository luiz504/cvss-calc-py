from dataclasses import dataclass


@dataclass(frozen=True)
class FormulaConstants:
    exploitability_coefficient: float = 8.22

    impact_coefficient_unchanged: float = 6.42

    impact_coefficient_changed: float = 7.52
    impact_changed_offset: float = 0.029
    impact_penalty_coefficient: float = 3.25
    impact_penalty_offset: float = 0.02
    impact_penalty_exponent: int = 15

    scope_changed_multiplier: float = 1.08
    min_score:int = 0
    max_score: int = 10


FORMULA = FormulaConstants()
