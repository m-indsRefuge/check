from copy import deepcopy

from check_validation.validate import validate_report


def issue_codes(report):
    return {issue.code for issue in validate_report(report)}


def test_minimal_report_passes_cross_field_validation(minimal_report):
    assert validate_report(minimal_report) == ()


def test_met_without_evidence_is_invalid(minimal_report):
    minimal_report["assessments"][0]["evidence_ids"] = []
    assert "MET_REQUIRES_EVIDENCE" in issue_codes(minimal_report)


def test_partial_without_evidence_is_invalid(minimal_report):
    minimal_report["assessments"][0]["verdict"] = "PARTIAL"
    minimal_report["assessments"][0]["evidence_ids"] = []
    assert "PARTIAL_REQUIRES_EVIDENCE" in issue_codes(minimal_report)


def test_contradicted_without_evidence_is_invalid(minimal_report):
    minimal_report["assessments"][0]["verdict"] = "CONTRADICTED"
    minimal_report["assessments"][0]["evidence_ids"] = []
    assert "CONTRADICTED_REQUIRES_EVIDENCE" in issue_codes(minimal_report)


def test_unverifiable_requires_uncertainty_note(minimal_report):
    assessment = minimal_report["assessments"][0]
    assessment["verdict"] = "UNVERIFIABLE"
    assessment["evidence_ids"] = []
    assessment["uncertainty_notes"] = []
    assert "UNVERIFIABLE_REQUIRES_LIMITATION" in issue_codes(minimal_report)


def test_missing_requires_complete_search_scope(minimal_report):
    assessment = minimal_report["assessments"][0]
    assessment["verdict"] = "MISSING"
    assessment["evidence_ids"] = []
    assessment["search_scope"]["complete"] = False
    assessment["search_scope"]["notes"] = ["Second page unavailable"]
    assert "MISSING_REQUIRES_COMPLETE_SEARCH_SCOPE" in issue_codes(minimal_report)


def test_absence_met_requires_complete_search_scope(minimal_report):
    minimal_report["criteria"][0]["requirement_kind"] = "ABSENCE"
    minimal_report["assessments"][0]["search_scope"]["complete"] = False
    assert "ABSENCE_MET_REQUIRES_COMPLETE_SEARCH_SCOPE" in issue_codes(minimal_report)


def test_related_evidence_alone_cannot_support_met(minimal_report):
    minimal_report["evidence"][0]["strength"] = "RELATED"
    assert "RELATED_CANNOT_SOLELY_SUPPORT_MET" in issue_codes(minimal_report)


def test_criterion_provenance_must_point_to_requirement_source(minimal_report):
    minimal_report["criteria"][0]["original_spans"] = ["SPAN-ART-001"]
    assert "CRITERION_PROVENANCE_REQUIRED" in issue_codes(minimal_report)


def test_evidence_provenance_must_point_to_artifact(minimal_report):
    minimal_report["evidence"][0]["source_spans"] = ["SPAN-REQ-001"]
    assert "EVIDENCE_PROVENANCE_REQUIRED" in issue_codes(minimal_report)


def test_unknown_reference_is_reported(minimal_report):
    minimal_report["assessments"][0]["evidence_ids"] = ["EVID-DOES-NOT-EXIST"]
    assert "REFERENCE_NOT_FOUND" in issue_codes(minimal_report)


def test_expression_cycle_is_rejected(minimal_report):
    report = deepcopy(minimal_report)
    report["requirement_expressions"] = [
        {
            "expression_id": "EXPR-A",
            "operator": "ALL_OF",
            "members": [{"kind": "EXPRESSION", "id": "EXPR-B"}],
            "minimum_satisfied": None,
            "condition": None,
            "provenance": ["SPAN-REQ-001"],
        },
        {
            "expression_id": "EXPR-B",
            "operator": "ALL_OF",
            "members": [{"kind": "EXPRESSION", "id": "EXPR-A"}],
            "minimum_satisfied": None,
            "condition": None,
            "provenance": ["SPAN-REQ-001"],
        },
    ]
    report["expression_results"] = []
    assert "EXPRESSION_CYCLE" in issue_codes(report)


def test_specific_artifact_scope_rejects_other_artifact_evidence(minimal_report):
    report = deepcopy(minimal_report)
    report["inputs"].append(
        {
            "document_id": "DOC-OTHER",
            "role": "ARTIFACT",
            "display_name": "cover-letter.txt",
            "media_type": "text/plain",
            "content_status": "AVAILABLE",
            "extraction_quality": "COMPLETE",
            "limitations": [],
        }
    )
    report["request"]["inputs"].append("DOC-OTHER")
    report["source_spans"].append(
        {
            "span_id": "SPAN-OTHER",
            "document_id": "DOC-OTHER",
            "location": "Paragraph 1",
            "exact_text": "Customer support experience.",
            "normalized_fact": None,
        }
    )
    report["criteria"][0]["artifact_scope"] = {
        "mode": "SPECIFIC_ARTIFACTS",
        "document_ids": ["DOC-ART"],
    }
    report["evidence"][0]["source_spans"] = ["SPAN-OTHER"]
    assert "ARTIFACT_SCOPE_VIOLATION" in issue_codes(report)


def test_duplicate_ids_are_rejected(minimal_report):
    minimal_report["inputs"].append(deepcopy(minimal_report["inputs"][0]))
    assert "DUPLICATE_ID" in issue_codes(minimal_report)
