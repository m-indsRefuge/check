from copy import deepcopy

import pytest

REPORT_ID = "REPORT-001"
REQ_DOC = "DOC-REQ"
ART_DOC = "DOC-ART"
REQ_SPAN = "SPAN-REQ-001"
ART_SPAN = "SPAN-ART-001"
CRITERION = "REQ-001"
EXPRESSION = "EXPR-001"
EVIDENCE = "EVID-001"
ASSESSMENT = "ASSESS-001"


def minimal_valid_report() -> dict:
    return {
        "report_id": REPORT_ID,
        "contract_version": "1.0",
        "request": {
            "request_id": "REQUEST-001",
            "inputs": [REQ_DOC, ART_DOC],
            "requested_scope": "Check the CV against the job description.",
            "user_instructions": [],
        },
        "inputs": [
            {
                "document_id": REQ_DOC,
                "role": "REQUIREMENT_SOURCE",
                "display_name": "job-description.txt",
                "media_type": "text/plain",
                "content_status": "AVAILABLE",
                "extraction_quality": "COMPLETE",
                "limitations": [],
            },
            {
                "document_id": ART_DOC,
                "role": "ARTIFACT",
                "display_name": "cv.txt",
                "media_type": "text/plain",
                "content_status": "AVAILABLE",
                "extraction_quality": "COMPLETE",
                "limitations": [],
            },
        ],
        "source_spans": [
            {
                "span_id": REQ_SPAN,
                "document_id": REQ_DOC,
                "location": "Requirements > paragraph 1",
                "exact_text": "At least three years of customer support experience.",
                "normalized_fact": ">= 3 years customer support experience",
            },
            {
                "span_id": ART_SPAN,
                "document_id": ART_DOC,
                "location": "Employment History",
                "exact_text": "Support Engineer — 2021 to 2025",
                "normalized_fact": "4 years support employment",
            },
        ],
        "criteria": [
            {
                "criterion_id": CRITERION,
                "parent_id": None,
                "normalized_requirement": "3+ years customer support experience",
                "original_spans": [REQ_SPAN],
                "strength": "REQUIRED",
                "effective_strength_if_applies": None,
                "interpretation_state": "CLEAR",
                "applicability": "NOT_CONDITIONAL",
                "requirement_kind": "QUANTITATIVE",
                "threshold": {"operator": "GTE", "value": 3, "unit": "years"},
                "prohibition": False,
                "source_precedence": None,
                "artifact_scope": {"mode": "ALL_ARTIFACTS", "document_ids": []},
            }
        ],
        "requirement_expressions": [
            {
                "expression_id": EXPRESSION,
                "operator": "SINGLE",
                "members": [{"kind": "CRITERION", "id": CRITERION}],
                "minimum_satisfied": None,
                "condition": None,
                "provenance": [REQ_SPAN],
            }
        ],
        "expression_results": [
            {
                "expression_id": EXPRESSION,
                "verdict": "MET",
                "member_assessment_ids": [ASSESSMENT],
                "reasoning": "The sole criterion is met.",
                "score_strength": "REQUIRED",
                "excluded_reason": None,
            }
        ],
        "evidence": [
            {
                "evidence_id": EVIDENCE,
                "criterion_ids": [CRITERION],
                "source_spans": [ART_SPAN],
                "strength": "DIRECT",
                "derived_value": None,
                "derivation": None,
                "reliability_notes": [],
            }
        ],
        "assessments": [
            {
                "assessment_id": ASSESSMENT,
                "criterion_id": CRITERION,
                "verdict": "MET",
                "evidence_ids": [EVIDENCE],
                "reasoning": "The artifact states four years in a support role.",
                "uncertainty_notes": [],
                "aggregation_status": None,
                "integrity_impacts": [],
                "repair_guidance": None,
                "search_scope": {
                    "document_ids": [ART_DOC],
                    "locations": ["Employment History"],
                    "complete": True,
                    "notes": [],
                },
            }
        ],
        "integrity_findings": [],
        "source_conflicts": [],
        "score_summary": {
            "required_coverage": 1.0,
            "preferred_coverage": None,
            "required_counts": {
                "met": 1,
                "partial": 0,
                "missing": 0,
                "contradicted": 0,
                "unverifiable": 0,
            },
            "preferred_counts": {
                "met": 0,
                "partial": 0,
                "missing": 0,
                "contradicted": 0,
                "unverifiable": 0,
            },
            "unspecified_counts": {
                "met": 0,
                "partial": 0,
                "missing": 0,
                "contradicted": 0,
                "unverifiable": 0,
            },
            "excluded_counts": {
                "unverifiable": 0,
                "does_not_apply": 0,
                "applicability_unknown": 0,
                "source_conflict": 0,
                "unspecified": 0,
            },
            "evaluability": {"required": "SUFFICIENT", "preferred": "INSUFFICIENT"},
            "threshold_used": 0.6,
            "suppression_reason": {
                "required": None,
                "preferred": "No preferred requirements were supplied.",
            },
        },
        "limitations": [],
        "advisories": [],
        "generated_at": "2026-08-29T12:00:00+02:00",
    }


@pytest.fixture
def minimal_report() -> dict:
    return deepcopy(minimal_valid_report())


@pytest.fixture
def repo_root():
    from pathlib import Path

    return Path(__file__).resolve().parents[2]
