import pytest

from check_validation.evaluate import compute_evaluation_metrics


def test_metrics_count_false_met_and_unnecessary_unverifiable():
    observations = [
        {
            "case_id": "a",
            "expectation_id": "1",
            "expected_verdict": "MET",
            "observed_verdict": "MET",
            "evidence_grounded": True,
            "requirement_overextracted": False,
            "unsupported_assumption": False,
            "logic_preserved": True,
            "report_contract_valid": True,
            "notes": "",
        },
        {
            "case_id": "b",
            "expectation_id": "2",
            "expected_verdict": "MISSING",
            "observed_verdict": "MET",
            "evidence_grounded": False,
            "requirement_overextracted": False,
            "unsupported_assumption": True,
            "logic_preserved": True,
            "report_contract_valid": True,
            "notes": "false positive",
        },
        {
            "case_id": "c",
            "expectation_id": "3",
            "expected_verdict": "MET",
            "observed_verdict": "UNVERIFIABLE",
            "evidence_grounded": True,
            "requirement_overextracted": True,
            "unsupported_assumption": False,
            "logic_preserved": False,
            "report_contract_valid": False,
            "notes": "too conservative",
        },
    ]
    metrics = compute_evaluation_metrics(observations)
    assert metrics.observations == 3
    assert metrics.verdict_accuracy == pytest.approx(1 / 3)
    assert metrics.false_met_count == 1
    assert metrics.observed_met_count == 2
    assert metrics.false_met_rate == 0.5
    assert metrics.unnecessary_unverifiable_count == 1
    assert metrics.observed_unverifiable_count == 1
    assert metrics.unnecessary_unverifiable_rate == 1.0
    assert metrics.requirement_overextraction_count == 1
    assert metrics.unsupported_assumption_count == 1
    assert metrics.logic_corruption_count == 1
    assert metrics.report_contract_violation_count == 1


def test_zero_denominators_return_none():
    metrics = compute_evaluation_metrics(
        [
            {
                "case_id": "a",
                "expectation_id": "1",
                "expected_verdict": "MISSING",
                "observed_verdict": "MISSING",
                "evidence_grounded": True,
                "requirement_overextracted": False,
                "unsupported_assumption": False,
                "logic_preserved": True,
                "report_contract_valid": True,
                "notes": "",
            }
        ]
    )
    assert metrics.false_met_rate is None
    assert metrics.unnecessary_unverifiable_rate is None


def test_empty_observations_have_none_accuracy():
    metrics = compute_evaluation_metrics([])
    assert metrics.observations == 0
    assert metrics.verdict_accuracy is None


def test_unknown_verdict_is_rejected():
    with pytest.raises(ValueError, match="invalid observed_verdict"):
        compute_evaluation_metrics(
            [
                {
                    "case_id": "a",
                    "expectation_id": "1",
                    "expected_verdict": "MET",
                    "observed_verdict": "LIKELY_MET",
                    "evidence_grounded": True,
                    "requirement_overextracted": False,
                    "unsupported_assumption": False,
                    "logic_preserved": True,
                    "report_contract_valid": True,
                    "notes": "",
                }
            ]
        )
