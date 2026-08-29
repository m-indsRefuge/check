from copy import deepcopy

from check_validation.expressions import derive_expression_results


def _criterion(criterion_id, span_id="SPAN-REQ-001", strength="REQUIRED"):
    return {
        "criterion_id": criterion_id,
        "parent_id": None,
        "normalized_requirement": criterion_id,
        "original_spans": [span_id],
        "strength": strength,
        "effective_strength_if_applies": None,
        "interpretation_state": "CLEAR",
        "applicability": "NOT_CONDITIONAL",
        "requirement_kind": "QUALITATIVE",
        "threshold": None,
        "prohibition": False,
        "source_precedence": None,
        "artifact_scope": {"mode": "ALL_ARTIFACTS", "document_ids": []},
    }


def _assessment(assessment_id, criterion_id, verdict):
    return {
        "assessment_id": assessment_id,
        "criterion_id": criterion_id,
        "verdict": verdict,
        "evidence_ids": [],
        "reasoning": verdict,
        "uncertainty_notes": ["unknown"] if verdict == "UNVERIFIABLE" else [],
        "aggregation_status": None,
        "integrity_impacts": [],
        "repair_guidance": None,
        "search_scope": {
            "document_ids": ["DOC-ART"],
            "locations": ["all"],
            "complete": True,
            "notes": [],
        },
    }


def _expression(expression_id, operator, members, minimum=None):
    return {
        "expression_id": expression_id,
        "operator": operator,
        "members": members,
        "minimum_satisfied": minimum,
        "condition": None,
        "provenance": ["SPAN-REQ-001"],
    }


def _report_with_members(minimal_report, verdicts, operator="ANY_OF", minimum=None):
    report = deepcopy(minimal_report)
    report["criteria"] = []
    report["assessments"] = []
    report["evidence"] = []
    members = []
    for index, verdict in enumerate(verdicts, start=1):
        criterion_id = f"REQ-{index}"
        assessment_id = f"ASSESS-{index}"
        report["criteria"].append(_criterion(criterion_id))
        report["assessments"].append(_assessment(assessment_id, criterion_id, verdict))
        members.append({"kind": "CRITERION", "id": criterion_id})
    report["requirement_expressions"] = [
        _expression("EXPR-ROOT", operator, members, minimum)
    ]
    report["expression_results"] = []
    return report


def test_any_of_is_met_when_one_alternative_is_met(minimal_report):
    report = _report_with_members(minimal_report, ["MET", "MISSING"])
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "MET"


def test_any_of_missing_alternative_does_not_create_partial_when_other_is_met(minimal_report):
    report = _report_with_members(minimal_report, ["MISSING", "MET"])
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "MET"
    assert result["member_assessment_ids"] == ["ASSESS-1", "ASSESS-2"]


def test_all_of_with_some_real_coverage_is_partial(minimal_report):
    report = _report_with_members(minimal_report, ["MET", "MISSING"], operator="ALL_OF")
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "PARTIAL"


def test_all_of_is_contradicted_when_any_required_member_conflicts(minimal_report):
    report = _report_with_members(minimal_report, ["MET", "CONTRADICTED"], operator="ALL_OF")
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "CONTRADICTED"


def test_at_least_n_of_is_unverifiable_when_unknown_paths_could_change_outcome(minimal_report):
    report = _report_with_members(
        minimal_report,
        ["MET", "UNVERIFIABLE", "MISSING"],
        operator="AT_LEAST_N_OF",
        minimum=2,
    )
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "UNVERIFIABLE"


def test_at_least_n_of_is_partial_when_partial_member_could_complete_threshold(minimal_report):
    report = _report_with_members(
        minimal_report,
        ["MET", "PARTIAL", "MISSING"],
        operator="AT_LEAST_N_OF",
        minimum=2,
    )
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "PARTIAL"


def test_nested_any_of_then_all_of_preserves_logic(minimal_report):
    report = _report_with_members(minimal_report, ["MISSING", "MET", "MET"])
    report["requirement_expressions"] = [
        _expression(
            "EXPR-CHOICE",
            "ANY_OF",
            [
                {"kind": "CRITERION", "id": "REQ-1"},
                {"kind": "CRITERION", "id": "REQ-2"},
            ],
        ),
        _expression(
            "EXPR-ROOT",
            "ALL_OF",
            [
                {"kind": "EXPRESSION", "id": "EXPR-CHOICE"},
                {"kind": "CRITERION", "id": "REQ-3"},
            ],
        ),
    ]
    results = {result["expression_id"]: result for result in derive_expression_results(report)}
    assert results["EXPR-CHOICE"]["verdict"] == "MET"
    assert results["EXPR-ROOT"]["verdict"] == "MET"
    assert results["EXPR-ROOT"]["member_assessment_ids"] == [
        "ASSESS-1",
        "ASSESS-2",
        "ASSESS-3",
    ]


def test_validate_report_detects_tampered_expression_result(minimal_report):
    from check_validation.validate import validate_report

    report = deepcopy(minimal_report)
    report["expression_results"][0]["verdict"] = "MISSING"
    codes = {issue.code for issue in validate_report(report)}
    assert "EXPRESSION_RESULT_MISMATCH" in codes
