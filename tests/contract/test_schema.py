from check_validation.schema import schema_issues


def test_minimal_report_matches_canonical_schema(minimal_report):
    assert schema_issues(minimal_report) == ()


def test_unknown_verdict_is_rejected(minimal_report):
    minimal_report["assessments"][0]["verdict"] = "PROBABLY_MET"
    issues = schema_issues(minimal_report)
    assert issues
    assert any("PROBABLY_MET" in issue.message for issue in issues)


def test_contract_version_is_required(minimal_report):
    del minimal_report["contract_version"]
    assert schema_issues(minimal_report)
