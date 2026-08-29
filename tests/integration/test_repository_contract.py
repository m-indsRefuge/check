import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from check_validation.models import CONTRACT_VERSION


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parents[2]


FORBIDDEN_IMPORTS = (
    "import openai",
    "from openai",
    "import agents",
    "from agents",
    "import requests",
    "from requests",
    "import httpx",
    "from httpx",
    "import anthropic",
    "from anthropic",
    "google.generativeai",
)


def test_plugin_package_and_runtime_files_are_present(repo_root):
    manifest = json.loads((repo_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "check"
    assert manifest["skills"] == "./skills/"
    assert manifest["version"] == "0.1.0"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    for path in [
        "skills/check/SKILL.md",
        "skills/check/references/contract.md",
        "skills/check/references/verdicts.md",
        "skills/check/references/report-format.md",
        "schemas/check-report.schema.json",
        "schemas/fixtures.schema.json",
    ]:
        assert (repo_root / path).is_file(), path


def test_contract_version_is_consistent(repo_root):
    assert CONTRACT_VERSION == "1.0"
    schema = json.loads((repo_root / "schemas/check-report.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["contract_version"]["const"] == CONTRACT_VERSION
    design = (repo_root / "docs/superpowers/specs/2026-08-29-check-v1-design.md").read_text(encoding="utf-8")
    assert f"Contract version: `{CONTRACT_VERSION}`" in design


def test_enforcement_addendum_records_machine_only_fields(repo_root):
    text = (
        repo_root
        / "docs/superpowers/specs/2026-08-29-check-v1-enforcement-addendum.md"
    ).read_text(encoding="utf-8")
    for phrase in [
        "Criterion.artifact_scope",
        "CriterionAssessment.search_scope",
        "RequirementExpression.members",
        "ScoreSummary.threshold_used",
        "does not change CHECK V1 semantic meaning",
    ]:
        assert phrase in text


def test_public_docs_no_longer_describe_a_pre_design_scaffold(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    architecture = (repo_root / "docs/architecture/README.md").read_text(encoding="utf-8")
    assert "Pre-design scaffold" not in readme
    assert "skills-first" in readme
    assert "offline" in readme.lower()
    assert "ChatGPT" in architecture
    assert "Python" in architecture
    assert "not called by the skill" in architecture


def test_fixture_schema_and_all_expected_files_validate(repo_root):
    schema = json.loads((repo_root / "schemas/fixtures.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    files = list((repo_root / "tests/fixtures").rglob("expected.json"))
    files += list((repo_root / "tests/adversarial").rglob("expected.json"))
    assert files
    for path in files:
        errors = list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))))
        assert not errors, f"{path}: {[error.message for error in errors]}"


def test_offline_validator_has_no_network_or_llm_sdk_imports(repo_root):
    source_root = repo_root / "src/check_validation"
    for path in source_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for forbidden in FORBIDDEN_IMPORTS:
            assert forbidden not in lowered, f"{path}: forbidden import {forbidden}"
