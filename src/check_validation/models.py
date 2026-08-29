from dataclasses import dataclass
from typing import Final

CONTRACT_VERSION: Final[str] = "1.0"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    observations: int
    verdict_accuracy: float | None
    false_met_count: int
    observed_met_count: int
    false_met_rate: float | None
    unnecessary_unverifiable_count: int
    observed_unverifiable_count: int
    unnecessary_unverifiable_rate: float | None
    requirement_overextraction_count: int
    unsupported_assumption_count: int
    logic_corruption_count: int
    report_contract_violation_count: int
