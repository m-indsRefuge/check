from copy import deepcopy

from check_validation.expressions import derive_expression_results
from check_validation.scoring import compute_score_summary, score_issues


def _set_verdict(report, verdict):
    assessment = report["assessments"][0]
    assessment["verdict"] = verdict
    assessment["uncertainty_notes"] = ["Cannot verify."] if verdict == "UNVERIFIABLE" else []
    if verdict in {"MISSING", "UNVERIFIABLE"}:
        assessment["evidence_ids"] = []
    report["expression_results"] = derive_expression_results(report)


def test_required_coverage_uses_root_expression_once(minimal_report):
    report = deepcopy(minimal_report)
    second = deepcopy(report["criteria"][0])
    second["criterion_id"] = "REQ-ALT"
    second["normalized_requirement"] = "Azure experience"
    report["criteria"][0]["normalized_requirement"] = "AWS experience"
    report["criteria"].append(second)

    second_assessment = deepcopy(report["assessments"][0])
    second_assessment["assessment_id"] = "ASSESS-ALT"
    second_assessment["criterion_id"] = "REQ-ALT"
    second_assessment["verdict"] = "MISSING"
    second_assessment["evidence_ids"] = []
    report["assessments"].append(second_assessment)

    report["requirement_expressions"] = [
        {
            "expression_id": "EXPR-OR",
            "operator": "ANY_OF",
            "members": [
                {"kind": "CRITERION", "id": "REQ-001"},
                {"kind": "CRITERION", "id": "REQ-ALT"},
            ],
            "minimum_satisfied": None,
            "condition": None,
            "provenance": ["SPAN-REQ-001"],
        }
    ]
    report["expression_results"] = derive_expression_results(report)

    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] == 1.0
    assert summary["required_counts"]["met"] == 1
    assert sum(summary["required_counts"].values()) == 1


def test_partial_scores_half(minimal_report):
    report = deepcopy(minimal_report)
    _set_verdict(report, "PARTIAL")
    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] == 0.5


def test_unverifiable_is_excluded_from_denominator(minimal_report):
    report = deepcopy(minimal_report)
    second = deepcopy(report["criteria"][0])
    second["criterion_id"] = "REQ-2"
    report["criteria"].append(second)
    second_assessment = deepcopy(report["assessments"][0])
    second_assessment["assessment_id"] = "ASSESS-2"
    second_assessment["criterion_id"] = "REQ-2"
    second_assessment["verdict"] = "UNVERIFIABLE"
    second_assessment["evidence_ids"] = []
    second_assessment["uncertainty_notes"] = ["Credential registry unavailable."]
    report["assessments"].append(second_assessment)
    report["requirement_expressions"] = [
        {
            "expression_id": "EXPR-1",
            "operator": "SINGLE",
            "members": [{"kind": "CRITERION", "id": "REQ-001"}],
            "minimum_satisfied": None,
            "condition": None,
            "provenance": ["SPAN-REQ-001"],
        },
        {
            "expression_id": "EXPR-2",
            "operator": "SINGLE",
            "members": [{"kind": "CRITERION", "id": "REQ-2"}],
            "minimum_satisfied": None,
            "condition": None,
            "provenance": ["SPAN-REQ-001"],
        },
    ]
    report["expression_results"] = derive_expression_results(report)

    summary = compute_score_summary(report, min_evaluable_ratio=0.50)
    assert summary["required_coverage"] == 1.0
    assert summary["required_counts"]["unverifiable"] == 1
    assert summary["excluded_counts"]["unverifiable"] == 1


def test_low_evaluability_withholds_percentage(minimal_report):
    report = deepcopy(minimal_report)
    report["criteria"] = []
    report["assessments"] = []
    report["requirement_expressions"] = []
    for index in range(5):
        criterion = deepcopy(minimal_report["criteria"][0])
        criterion["criterion_id"] = f"REQ-{index}"
        report["criteria"].append(criterion)
        assessment = deepcopy(minimal_report["assessments"][0])
        assessment["assessment_id"] = f"ASSESS-{index}"
        assessment["criterion_id"] = f"REQ-{index}"
        if index:
            assessment["verdict"] = "UNVERIFIABLE"
            assessment["evidence_ids"] = []
            assessment["uncertainty_notes"] = ["Cannot verify."]
        report["assessments"].append(assessment)
        report["requirement_expressions"].append(
            {
                "expression_id": f"EXPR-{index}",
                "operator": "SINGLE",
                "members": [{"kind": "CRITERION", "id": f"REQ-{index}"}],
                "minimum_satisfied": None,
                "condition": None,
                "provenance": ["SPAN-REQ-001"],
            }
        )
    report["expression_results"] = derive_expression_results(report)

    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["evaluability"]["required"] == "INSUFFICIENT"
    assert summary["required_coverage"] is None
    assert "1 of 5" in summary["suppression_reason"]["required"]


def test_score_issues_detect_tampered_coverage(minimal_report):
    report = deepcopy(minimal_report)
    report["score_summary"]["required_coverage"] = 0.25
    issues = score_issues(report)
    assert {issue.code for issue in issues} == {"SCORE_SUMMARY_MISMATCH"}


def test_does_not_apply_is_excluded_from_scoring(minimal_report):
    report = deepcopy(minimal_report)
    criterion = report["criteria"][0]
    criterion["strength"] = "CONDITIONAL"
    criterion["effective_strength_if_applies"] = "REQUIRED"
    criterion["applicability"] = "DOES_NOT_APPLY"
    report["expression_results"] = derive_expression_results(report)
    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] is None
    assert summary["excluded_counts"]["does_not_apply"] == 1


def test_applicability_unknown_is_excluded_from_scoring(minimal_report):
    report = deepcopy(minimal_report)
    criterion = report["criteria"][0]
    criterion["strength"] = "CONDITIONAL"
    criterion["effective_strength_if_applies"] = "REQUIRED"
    criterion["applicability"] = "APPLICABILITY_UNKNOWN"
    report["expression_results"] = derive_expression_results(report)
    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] is None
    assert summary["excluded_counts"]["applicability_unknown"] == 1


def test_unresolved_source_conflict_is_excluded(minimal_report):
    report = deepcopy(minimal_report)
    report["source_conflicts"] = [
        {
            "conflict_id": "CONFLICT-1",
            "source_spans": ["SPAN-REQ-001", "SPAN-ART-001"],
            "affected_criterion_ids": ["REQ-001"],
            "affected_expression_ids": [],
            "precedence_considered": [],
            "resolved": False,
            "resolution_basis": None,
        }
    ]
    report["expression_results"] = derive_expression_results(report)
    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] is None
    assert summary["excluded_counts"]["source_conflict"] == 1


def test_unspecified_strength_never_enters_required_or_preferred_coverage(minimal_report):
    report = deepcopy(minimal_report)
    report["criteria"][0]["strength"] = "UNSPECIFIED"
    report["expression_results"] = derive_expression_results(report)
    summary = compute_score_summary(report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] is None
    assert summary["preferred_coverage"] is None
    assert summary["unspecified_counts"]["met"] == 1
    assert summary["excluded_counts"]["unspecified"] == 1
