def test_style_reference_defines_helpful_expert_voice(repo_root):
    path = repo_root / "skills/check/references/style.md"
    assert path.is_file()

    text = path.read_text(encoding="utf-8")
    for phrase in [
        "Helpful Expert",
        "Lead with the answer",
        "plain professional English",
        "Explain why in ordinary language",
        "what would resolve the gap",
        "Do not narrate internal pipeline mechanics",
    ]:
        assert phrase in text


def test_production_skill_reads_style_reference(repo_root):
    text = (repo_root / "skills/check/SKILL.md").read_text(encoding="utf-8")
    assert "references/style.md" in text


def test_human_report_uses_stacked_blocks_not_markdown_tables(repo_root):
    text = (repo_root / "skills/check/references/report-format.md").read_text(encoding="utf-8")
    assert "stacked requirement blocks" in text
    assert "Do not use Markdown tables" in text
    assert "**Evidence:**" in text
    assert "**Reason:**" in text


def test_human_report_uses_short_provenance(repo_root):
    text = (repo_root / "skills/check/references/report-format.md").read_text(encoding="utf-8")
    assert "`artifact.txt:3`" in text
    assert "Do not show absolute local filesystem paths" in text


def test_source_conflict_branches_are_diagnostic_not_peer_verdicts(repo_root):
    text = (repo_root / "skills/check/references/report-format.md").read_text(encoding="utf-8")
    for phrase in [
        "Diagnostic detail",
        "diagnostic only",
        "not scored separately",
        "governing obligation remains `UNVERIFIABLE`",
    ]:
        assert phrase in text
