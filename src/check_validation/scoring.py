from collections.abc import Mapping
from typing import Any

from .expressions import derive_expression_results
from .models import ValidationIssue

VERDICT_WEIGHT = {
    "MET": 1.0,
    "PARTIAL": 0.5,
    "MISSING": 0.0,
    "CONTRADICTED": 0.0,
}


def _empty_counts() -> dict[str, int]:
    return {
        "met": 0,
        "partial": 0,
        "missing": 0,
        "contradicted": 0,
        "unverifiable": 0,
    }


def _root_expression_ids(report: Mapping[str, Any]) -> list[str]:
    referenced = {
        member["id"]
        for expression in report["requirement_expressions"]
        for member in expression["members"]
        if member["kind"] == "EXPRESSION"
    }
    return [
        expression["expression_id"]
        for expression in report["requirement_expressions"]
        if expression["expression_id"] not in referenced
    ]


def _group_summary(
    results: list[Mapping[str, Any]], strength: str, threshold: float
) -> tuple[float | None, dict[str, int], str, str | None]:
    group = [result for result in results if result["score_strength"] == strength]
    counts = _empty_counts()
    for result in group:
        counts[result["verdict"].lower()] += 1

    applicable = [result for result in group if result.get("excluded_reason") is None]
    scoreable = [result for result in applicable if result["verdict"] != "UNVERIFIABLE"]
    if not applicable:
        return None, counts, "INSUFFICIENT", f"No {strength.lower()} requirements were supplied."

    evaluable_ratio = len(scoreable) / len(applicable)
    if evaluable_ratio < threshold:
        return (
            None,
            counts,
            "INSUFFICIENT",
            f"Only {len(scoreable)} of {len(applicable)} {strength.lower()} requirements could be evaluated reliably.",
        )

    if not scoreable:
        return (
            None,
            counts,
            "INSUFFICIENT",
            f"No {strength.lower()} requirements could be evaluated reliably.",
        )

    numerator = sum(VERDICT_WEIGHT[result["verdict"]] for result in scoreable)
    return numerator / len(scoreable), counts, "SUFFICIENT", None


def compute_score_summary(
    report: Mapping[str, Any], *, min_evaluable_ratio: float
) -> dict[str, Any]:
    if not 0 < min_evaluable_ratio <= 1:
        raise ValueError("min_evaluable_ratio must be greater than 0 and at most 1")

    derived = derive_expression_results(report)
    by_id = {result["expression_id"]: result for result in derived}
    root_results = [by_id[expression_id] for expression_id in _root_expression_ids(report)]

    required_coverage, required_counts, required_eval, required_reason = _group_summary(
        root_results, "REQUIRED", min_evaluable_ratio
    )
    preferred_coverage, preferred_counts, preferred_eval, preferred_reason = _group_summary(
        root_results, "PREFERRED", min_evaluable_ratio
    )
    _, unspecified_counts, _, _ = _group_summary(
        root_results, "UNSPECIFIED", min_evaluable_ratio
    )

    excluded_counts = {
        "unverifiable": sum(
            result["verdict"] == "UNVERIFIABLE" for result in root_results
        ),
        "does_not_apply": sum(
            result.get("excluded_reason") == "DOES_NOT_APPLY" for result in root_results
        ),
        "applicability_unknown": sum(
            result.get("excluded_reason") == "APPLICABILITY_UNKNOWN" for result in root_results
        ),
        "source_conflict": sum(
            result.get("excluded_reason") == "SOURCE_CONFLICT" for result in root_results
        ),
        "unspecified": sum(result["score_strength"] == "UNSPECIFIED" for result in root_results),
    }

    return {
        "required_coverage": required_coverage,
        "preferred_coverage": preferred_coverage,
        "required_counts": required_counts,
        "preferred_counts": preferred_counts,
        "unspecified_counts": unspecified_counts,
        "excluded_counts": excluded_counts,
        "evaluability": {
            "required": required_eval,
            "preferred": preferred_eval,
        },
        "threshold_used": min_evaluable_ratio,
        "suppression_reason": {
            "required": required_reason,
            "preferred": preferred_reason,
        },
    }


def score_issues(report: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
    threshold = report["score_summary"]["threshold_used"]
    expected = compute_score_summary(report, min_evaluable_ratio=threshold)
    actual = report["score_summary"]
    if expected == actual:
        return ()
    return (
        ValidationIssue(
            code="SCORE_SUMMARY_MISMATCH",
            path="/score_summary",
            message="Score summary does not match the deterministic CHECK scoring calculation.",
        ),
    )
