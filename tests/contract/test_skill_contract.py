import re


def test_contract_reference_contains_all_28_rules_exactly_once(repo_root):
    path = repo_root / "skills/check/references/contract.md"
    text = path.read_text(encoding="utf-8")
    headings = re.findall(r"^### Rule (\d+) —", text, flags=re.MULTILINE)
    assert headings == [str(number) for number in range(1, 29)]


def test_verdict_reference_defines_exact_five_verdicts(repo_root):
    text = (repo_root / "skills/check/references/verdicts.md").read_text(encoding="utf-8")
    verdict_headings = re.findall(
        r"^### `(MET|PARTIAL|MISSING|CONTRADICTED|UNVERIFIABLE)`$",
        text,
        flags=re.MULTILINE,
    )
    assert verdict_headings == [
        "MET",
        "PARTIAL",
        "MISSING",
        "CONTRADICTED",
        "UNVERIFIABLE",
    ]
    for phrase in [
        "Cannot evaluate reliably -> `UNVERIFIABLE`",
        "Explicit conflicting evidence -> `CONTRADICTED`",
        "Fully satisfied -> `MET`",
        "Meaningful incomplete evidence -> `PARTIAL`",
        "Otherwise, after complete search -> `MISSING`",
    ]:
        assert phrase in text


def test_report_format_defines_five_human_sections_in_order(repo_root):
    text = (repo_root / "skills/check/references/report-format.md").read_text(encoding="utf-8")
    expected = [
        "1. Summary",
        "2. Priority Gaps",
        "3. Verification Matrix",
        "4. Integrity and Limitations",
        "5. Advisory Observations",
    ]
    positions = [text.index(item) for item in expected]
    assert positions == sorted(positions)
