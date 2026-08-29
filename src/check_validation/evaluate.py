from collections.abc import Mapping, Sequence
from typing import Any

from .models import EvaluationMetrics

_VERDICTS = {"MET", "PARTIAL", "MISSING", "CONTRADICTED", "UNVERIFIABLE"}
_REQUIRED_KEYS = {
    "case_id",
    "expectation_id",
    "expected_verdict",
    "observed_verdict",
    "evidence_grounded",
    "requirement_overextracted",
    "unsupported_assumption",
    "logic_preserved",
    "report_contract_valid",
    "notes",
}
_BOOL_KEYS = {
    "evidence_grounded",
    "requirement_overextracted",
    "unsupported_assumption",
    "logic_preserved",
    "report_contract_valid",
}


def _validate_observation(observation: Mapping[str, Any], index: int) -> None:
    missing = _REQUIRED_KEYS - set(observation)
    if missing:
        raise ValueError(f"observation {index} missing required keys: {sorted(missing)}")
    expected = observation["expected_verdict"]
    observed = observation["observed_verdict"]
    if expected not in _VERDICTS:
        raise ValueError(f"observation {index} has invalid expected_verdict: {expected!r}")
    if observed not in _VERDICTS:
        raise ValueError(f"observation {index} has invalid observed_verdict: {observed!r}")
    for key in _BOOL_KEYS:
        if not isinstance(observation[key], bool):
            raise TypeError(f"observation {index} field {key!r} must be boolean")


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def compute_evaluation_metrics(
    observations: Sequence[Mapping[str, Any]],
) -> EvaluationMetrics:
    for index, observation in enumerate(observations):
        _validate_observation(observation, index)

    total = len(observations)
    correct = sum(
        observation["expected_verdict"] == observation["observed_verdict"]
        for observation in observations
    )
    observed_met = sum(observation["observed_verdict"] == "MET" for observation in observations)
    false_met = sum(
        observation["observed_verdict"] == "MET"
        and observation["expected_verdict"] != "MET"
        for observation in observations
    )
    observed_unverifiable = sum(
        observation["observed_verdict"] == "UNVERIFIABLE" for observation in observations
    )
    unnecessary_unverifiable = sum(
        observation["observed_verdict"] == "UNVERIFIABLE"
        and observation["expected_verdict"] != "UNVERIFIABLE"
        for observation in observations
    )

    return EvaluationMetrics(
        observations=total,
        verdict_accuracy=_ratio(correct, total),
        false_met_count=false_met,
        observed_met_count=observed_met,
        false_met_rate=_ratio(false_met, observed_met),
        unnecessary_unverifiable_count=unnecessary_unverifiable,
        observed_unverifiable_count=observed_unverifiable,
        unnecessary_unverifiable_rate=_ratio(
            unnecessary_unverifiable, observed_unverifiable
        ),
        requirement_overextraction_count=sum(
            observation["requirement_overextracted"] for observation in observations
        ),
        unsupported_assumption_count=sum(
            observation["unsupported_assumption"] for observation in observations
        ),
        logic_corruption_count=sum(
            not observation["logic_preserved"] for observation in observations
        ),
        report_contract_violation_count=sum(
            not observation["report_contract_valid"] for observation in observations
        ),
    )
