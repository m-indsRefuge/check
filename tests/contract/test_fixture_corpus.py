import json
from pathlib import Path

from jsonschema import Draft202012Validator

DOMAINS = {
    "cv-job",
    "essay-rubric",
    "proposal-brief",
    "software-acceptance",
    "report-deliverables",
    "eligibility",
    "policy",
}

RISK_FAMILIES = {
    "goalpost-expansion",
    "plausibility-trap",
    "false-absence",
    "overlap-double-counting",
    "ambiguity-invention",
    "documentary-vs-reality",
    "logical-or-corruption",
    "duplicate-requirement-inflation",
    "incomplete-extraction-as-missing",
    "source-conflict",
    "artifact-integrity",
    "conditional-applicability",
}


def _fixture_dirs(root: Path) -> list[Path]:
    return sorted(path.parent for path in root.rglob("expected.json"))


def test_fixture_schema_is_valid_draft_2020_12(repo_root):
    schema_path = repo_root / "schemas/fixtures.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_all_fixture_directories_have_required_files_and_valid_metadata(repo_root):
    schema = json.loads((repo_root / "schemas/fixtures.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    roots = [repo_root / "tests/fixtures", repo_root / "tests/adversarial"]
    fixture_dirs = [directory for root in roots for directory in _fixture_dirs(root)]
    assert fixture_dirs

    for directory in fixture_dirs:
        for filename in ["requirements.txt", "artifact.txt", "expected.json", "README.md"]:
            assert (directory / filename).is_file(), f"{directory}: missing {filename}"
        expected = json.loads((directory / "expected.json").read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(expected))
        assert not errors, f"{directory}: {[error.message for error in errors]}"


def test_all_required_baseline_domains_exist(repo_root):
    found = set()
    for path in (repo_root / "tests/fixtures").rglob("expected.json"):
        expected = json.loads(path.read_text(encoding="utf-8"))
        found.add(expected["domain"])
    assert DOMAINS <= found


def test_all_adversarial_risk_families_exist(repo_root):
    found = set()
    for path in (repo_root / "tests/adversarial").rglob("expected.json"):
        expected = json.loads(path.read_text(encoding="utf-8"))
        found.update(expected["risk_tags"])
    assert RISK_FAMILIES <= found
