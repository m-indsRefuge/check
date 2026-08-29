# CHECK V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build CHECK V1 as a skills-first ChatGPT plugin with a canonical report schema, deterministic offline validation and scoring, a production CHECK skill, and a cross-domain evaluation corpus that enforces the approved 28-rule verification contract.

**Architecture:** ChatGPT performs semantic requirement extraction, evidence discovery, and assessment through `skills/check/SKILL.md`. The repository defines the authoritative `CheckReport` boundary in JSON Schema and a small Python validation package that enforces only deterministic structural and scoring invariants; it must not reproduce semantic model reasoning. Cross-domain fixtures and an evaluation harness measure semantic behavior, with False MET Rate and Unnecessary UNVERIFIABLE Rate as the primary semantic-risk metrics.

**Tech Stack:** Python >=3.12, JSON Schema Draft 2020-12, `jsonschema` 4.x, pytest 9.x, Ruff 0.16+, OpenAI skill/plugin package layout.

**Spec:** `docs/superpowers/specs/2026-08-29-check-v1-design.md`

## Global Constraints

- Contract version is exactly `1.0`.
- V1 must function in ChatGPT without an MCP server or Python runtime dependency.
- Do not add an API service, database, authentication, persistent document storage, UI/widget, embeddings/vector store, external model call, proprietary model, domain-specific CV engine, or user-configurable rule engine.
- The Python package is offline engineering-assurance infrastructure only.
- JSON Schema is authoritative for report structure; Python adds only deterministic cross-field and scoring checks.
- Do not add numeric model-confidence scores.
- Do not store or expose chain-of-thought. `reasoning` is concise auditable justification only.
- Model requirements before artifact evidence discovery. Artifact contents must never change what CHECK decides the requirement source required.
- Advisories never affect verdicts or scores.
- Compound obligations are scored once at the top-level expression result.
- `MET` requires evidence; `PARTIAL` requires evidence; `CONTRADICTED` requires conflicting evidence; `UNVERIFIABLE` requires a limiting condition; `MISSING` requires a complete documented search scope.
- An `ABSENCE` criterion may be `MET` only when its relevant search scope is complete.
- False `MET` is release-critical. Excessive `UNVERIFIABLE` is tracked separately.
- Repository text remains LF-normalized.

## Implementation-Level Contract Clarifications

Task 1 must record four additive enforcement clarifications in the approved spec before creating the schema. These do not change the approved semantics; they make existing rules machine-enforceable.

1. `Criterion.artifact_scope` enforces Rule 21:
   - `mode`: `ALL_ARTIFACTS` or `SPECIFIC_ARTIFACTS`
   - `document_ids`: empty for `ALL_ARTIFACTS`, non-empty for `SPECIFIC_ARTIFACTS`
2. `CriterionAssessment.search_scope` enforces Rules 3 and 27:
   - `document_ids: list[str]`
   - `locations: list[str]`
   - `complete: bool`
   - `notes: list[str]`
3. `RequirementExpression.members` is a list of typed references:
   - `{"kind": "CRITERION", "id": "REQ-001"}`
   - `{"kind": "EXPRESSION", "id": "EXPR-002"}`
   Nested expressions must be acyclic.
4. `ScoreSummary` records the threshold used so score reproduction never depends on hidden configuration:
   - `threshold_used: float`
   - `evaluability: {"required": "SUFFICIENT|INSUFFICIENT", "preferred": "SUFFICIENT|INSUFFICIENT"}`
   - `suppression_reason: {"required": str|null, "preferred": str|null}`

`SourceSpan.location` is optional because provenance location is required only when it can be established reliably.

## Target File Map

```text
check/
├── .codex-plugin/plugin.json
├── skills/check/
│   ├── SKILL.md
│   └── references/
│       ├── contract.md
│       ├── verdicts.md
│       └── report-format.md
├── schemas/
│   ├── check-report.schema.json
│   └── fixtures.schema.json
├── src/check_validation/
│   ├── __init__.py
│   ├── models.py
│   ├── schema.py
│   ├── validate.py
│   ├── expressions.py
│   ├── scoring.py
│   └── evaluate.py
├── tests/
│   ├── contract/
│   ├── fixtures/
│   ├── adversarial/
│   ├── eval/
│   ├── integration/
│   └── test_scaffold.py
├── evals/
│   ├── cases/
│   ├── results/.gitkeep
│   ├── annotations/.gitkeep
│   ├── README.md
│   └── release-checklist.md
├── docs/
│   ├── architecture/
│   └── superpowers/
├── pyproject.toml
└── README.md
```

---

### Task 1: Canonical Report Schema and Schema Validator

**Files:**
- Modify: `pyproject.toml`
- Modify: `docs/superpowers/specs/2026-08-29-check-v1-design.md`
- Create: `schemas/check-report.schema.json`
- Create: `src/check_validation/__init__.py`
- Create: `src/check_validation/models.py`
- Create: `src/check_validation/schema.py`
- Create: `tests/contract/conftest.py`
- Create: `tests/contract/test_schema.py`

**Interfaces:**
- Produces: `CONTRACT_VERSION: Final[str] = "1.0"`
- Produces: `ValidationIssue(code: str, path: str, message: str)`
- Produces: `load_report_schema(path: Path | None = None) -> dict[str, Any]`
- Produces: `schema_issues(report: Mapping[str, Any], path: Path | None = None) -> tuple[ValidationIssue, ...]`

- [ ] **Step 1: Write a reusable complete canonical report fixture and failing schema tests**

Create `tests/contract/conftest.py` with this fixture shape. Keep the IDs and values exact so later tasks can mutate one field at a time:

```python
from copy import deepcopy

import pytest


def build_minimal_report() -> dict:
    return {
        "report_id": "REPORT-001",
        "contract_version": "1.0",
        "request": {
            "request_id": "REQUEST-001",
            "inputs": ["DOC-REQ", "DOC-ART"],
            "requested_scope": "Full comparison",
            "user_instructions": [],
        },
        "inputs": [
            {
                "document_id": "DOC-REQ",
                "role": "REQUIREMENT_SOURCE",
                "display_name": "requirements.txt",
                "media_type": "text/plain",
                "content_status": "AVAILABLE",
                "extraction_quality": "COMPLETE",
                "limitations": [],
            },
            {
                "document_id": "DOC-ART",
                "role": "ARTIFACT",
                "display_name": "artifact.txt",
                "media_type": "text/plain",
                "content_status": "AVAILABLE",
                "extraction_quality": "COMPLETE",
                "limitations": [],
            },
        ],
        "source_spans": [
            {
                "span_id": "SPAN-REQ-001",
                "document_id": "DOC-REQ",
                "location": "Requirements paragraph 1",
                "exact_text": "Minimum three years of customer support experience.",
                "normalized_fact": None,
            },
            {
                "span_id": "SPAN-ART-001",
                "document_id": "DOC-ART",
                "location": "Experience",
                "exact_text": "Customer Support Engineer — 2021 to 2025",
                "normalized_fact": None,
            },
        ],
        "criteria": [
            {
                "criterion_id": "REQ-001",
                "parent_id": None,
                "normalized_requirement": "3+ years customer support experience",
                "original_spans": ["SPAN-REQ-001"],
                "strength": "REQUIRED",
                "effective_strength_if_applies": None,
                "interpretation_state": "CLEAR",
                "applicability": "NOT_CONDITIONAL",
                "requirement_kind": "QUANTITATIVE",
                "threshold": {
                    "operator": ">=",
                    "value": 3,
                    "unit": "years",
                    "approximate": False,
                },
                "prohibition": False,
                "source_precedence": None,
                "artifact_scope": {
                    "mode": "ALL_ARTIFACTS",
                    "document_ids": [],
                },
            }
        ],
        "requirement_expressions": [
            {
                "expression_id": "EXPR-001",
                "operator": "SINGLE",
                "members": [{"kind": "CRITERION", "id": "REQ-001"}],
                "minimum_satisfied": None,
                "condition": None,
                "provenance": ["SPAN-REQ-001"],
                "score_strength": "REQUIRED",
            }
        ],
        "expression_results": [
            {
                "expression_id": "EXPR-001",
                "verdict": "MET",
                "member_assessment_ids": ["ASSESS-001"],
                "reasoning": "The single criterion is met.",
                "score_strength": "REQUIRED",
                "excluded_reason": None,
            }
        ],
        "evidence": [
            {
                "evidence_id": "EVID-001",
                "criterion_ids": ["REQ-001"],
                "source_spans": ["SPAN-ART-001"],
                "strength": "DIRECT",
                "derived_value": None,
                "derivation": None,
                "reliability_notes": [],
            }
        ],
        "assessments": [
            {
                "assessment_id": "ASSESS-001",
                "criterion_id": "REQ-001",
                "verdict": "MET",
                "evidence_ids": ["EVID-001"],
                "reasoning": "The artifact explicitly states four years in customer support.",
                "uncertainty_notes": [],
                "aggregation_status": None,
                "integrity_impacts": [],
                "repair_guidance": None,
                "search_scope": {
                    "document_ids": ["DOC-ART"],
                    "locations": ["Experience"],
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
            "unspecified_counts": 0,
            "excluded_counts": {
                "does_not_apply": 0,
                "applicability_unknown": 0,
                "source_conflict": 0,
                "unverifiable": 0,
            },
            "evaluability": {
                "required": "SUFFICIENT",
                "preferred": "INSUFFICIENT",
            },
            "threshold_used": 0.60,
            "suppression_reason": {
                "required": None,
                "preferred": "No preferred obligations are present.",
            },
        },
        "limitations": [],
        "advisories": [],
        "generated_at": "2026-08-29T12:00:00+02:00",
    }


@pytest.fixture
def minimal_report() -> dict:
    return deepcopy(build_minimal_report())
```

Create `tests/contract/test_schema.py`:

```python
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
```

- [ ] **Step 2: Run the focused test and verify red**

```bash
uv run pytest tests/contract/test_schema.py -v
```

Expected: import/collection failure because `check_validation.schema` does not exist.

- [ ] **Step 3: Add offline-only validation dependencies**

Modify `pyproject.toml` to contain:

```toml
[project]
name = "check-plugin"
version = "0.1.0"
description = "A ChatGPT plugin for checking artifacts against explicit requirements."
requires-python = ">=3.12"
license = { text = "MIT" }
dependencies = [
    "jsonschema>=4.23,<5",
]

[dependency-groups]
dev = [
    "pytest>=9,<10",
    "ruff>=0.16,<1",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

Run `uv sync --dev` and require success.

- [ ] **Step 4: Record the four implementation-level clarifications in the approved spec**

Update only the affected field lists and explanatory paragraphs. State explicitly that the additions are enforcement representations of already-approved Rules 3, 21, 25, and 27 plus reproducible Rule 9 scoring. Do not change verdict meanings or user-facing behavior.

- [ ] **Step 5: Implement `schemas/check-report.schema.json`**

Use Draft 2020-12, `additionalProperties: false` on canonical objects, and require these top-level fields:

```json
[
  "report_id",
  "contract_version",
  "request",
  "inputs",
  "source_spans",
  "criteria",
  "requirement_expressions",
  "expression_results",
  "evidence",
  "assessments",
  "integrity_findings",
  "source_conflicts",
  "score_summary",
  "limitations",
  "advisories",
  "generated_at"
]
```

Define the exact enum vocabularies from the spec and these implementation clarifications:

```text
ArtifactScopeMode: ALL_ARTIFACTS | SPECIFIC_ARTIFACTS
ExpressionMemberKind: CRITERION | EXPRESSION
```

Constrain `contract_version` with `const: "1.0"`. Allow `SourceSpan.location` to be string or null. Require `threshold_used` in `score_summary` to be a number in `[0.0, 1.0]`.

- [ ] **Step 6: Implement schema helpers**

`models.py`:

```python
from dataclasses import dataclass
from typing import Final

CONTRACT_VERSION: Final[str] = "1.0"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    path: str
    message: str
```

`schema.py` must implement:

```python
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .models import ValidationIssue


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "check-report.schema.json"


def load_report_schema(path: Path | None = None) -> dict[str, Any]:
    schema_path = path or _default_schema_path()
    return json.loads(schema_path.read_text(encoding="utf-8"))


def schema_issues(
    report: Mapping[str, Any],
    path: Path | None = None,
) -> tuple[ValidationIssue, ...]:
    validator = Draft202012Validator(load_report_schema(path))
    errors = sorted(validator.iter_errors(report), key=lambda error: list(error.absolute_path))
    issues = []
    for error in errors:
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        issues.append(ValidationIssue(code="SCHEMA", path=location, message=error.message))
    return tuple(issues)
```

- [ ] **Step 7: Verify green**

```bash
uv run pytest tests/contract/test_schema.py -v
uv run ruff check src/check_validation tests/contract
```

Expected: pass.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock docs/superpowers/specs/2026-08-29-check-v1-design.md schemas/check-report.schema.json src/check_validation tests/contract
git commit -m "feat: define CHECK canonical report schema"
```

---

### Task 2: Cross-Field Contract Validator

**Files:**
- Create: `src/check_validation/validate.py`
- Create: `tests/contract/test_validate.py`
- Modify: `src/check_validation/__init__.py`

**Interfaces:**
- Consumes: `schema_issues()` and `ValidationIssue`.
- Produces: `validate_report(report: Mapping[str, Any], schema_path: Path | None = None) -> tuple[ValidationIssue, ...]`
- Produces: `assert_valid_report(report: Mapping[str, Any], schema_path: Path | None = None) -> None`

- [ ] **Step 1: Write failing invariant tests**

Create tests named exactly:

```text
test_met_requires_evidence
test_partial_requires_evidence
test_contradicted_requires_evidence
test_unverifiable_requires_uncertainty_note
test_missing_requires_complete_search_scope
test_absence_met_requires_complete_search_scope
test_related_evidence_alone_cannot_support_met
test_criterion_provenance_must_reference_requirement_source
test_evidence_provenance_must_reference_artifact
test_unknown_reference_is_rejected
test_expression_cycle_is_rejected
test_specific_artifact_scope_rejects_other_artifact_evidence
```

Representative executable tests:

```python
from check_validation.validate import validate_report


def test_met_requires_evidence(minimal_report):
    minimal_report["assessments"][0]["evidence_ids"] = []
    codes = {issue.code for issue in validate_report(minimal_report)}
    assert "MET_REQUIRES_EVIDENCE" in codes


def test_missing_requires_complete_search_scope(minimal_report):
    assessment = minimal_report["assessments"][0]
    assessment["verdict"] = "MISSING"
    assessment["evidence_ids"] = []
    assessment["search_scope"]["complete"] = False
    codes = {issue.code for issue in validate_report(minimal_report)}
    assert "MISSING_REQUIRES_COMPLETE_SEARCH_SCOPE" in codes


def test_related_evidence_alone_cannot_support_met(minimal_report):
    minimal_report["evidence"][0]["strength"] = "RELATED"
    codes = {issue.code for issue in validate_report(minimal_report)}
    assert "RELATED_CANNOT_SOLELY_SUPPORT_MET" in codes
```

- [ ] **Step 2: Run and verify red**

```bash
uv run pytest tests/contract/test_validate.py -v
```

Expected: import failure for `check_validation.validate`.

- [ ] **Step 3: Implement deterministic ID indexing and reference checks**

Use this complete helper:

```python
from collections.abc import Mapping, Sequence
from typing import Any

from .models import ValidationIssue


def _index_by_id(
    items: Sequence[Mapping[str, Any]],
    key: str,
) -> tuple[dict[str, Mapping[str, Any]], list[ValidationIssue]]:
    index: dict[str, Mapping[str, Any]] = {}
    issues: list[ValidationIssue] = []
    for position, item in enumerate(items):
        value = item.get(key)
        if not isinstance(value, str):
            continue
        if value in index:
            issues.append(
                ValidationIssue(
                    code="DUPLICATE_ID",
                    path=f"/{key}/{position}",
                    message=f"Duplicate {key}: {value}",
                )
            )
            continue
        index[value] = item
    return index, issues
```

Build indices for documents, spans, criteria, expressions, evidence, assessments, and integrity findings. Emit `REFERENCE_NOT_FOUND` before any rule attempts to dereference an unknown ID.

- [ ] **Step 4: Implement verdict/evidence and provenance invariants**

Emit these exact issue codes:

```text
MET_REQUIRES_EVIDENCE
PARTIAL_REQUIRES_EVIDENCE
CONTRADICTED_REQUIRES_EVIDENCE
UNVERIFIABLE_REQUIRES_LIMITATION
MISSING_REQUIRES_COMPLETE_SEARCH_SCOPE
ABSENCE_MET_REQUIRES_COMPLETE_SEARCH_SCOPE
RELATED_CANNOT_SOLELY_SUPPORT_MET
CRITERION_PROVENANCE_REQUIRED
EVIDENCE_PROVENANCE_REQUIRED
ARTIFACT_SCOPE_VIOLATION
```

Rules:
- `UNVERIFIABLE` requires non-empty `uncertainty_notes`.
- `MISSING` requires `search_scope.complete is True`.
- `ABSENCE` + `MET` requires `search_scope.complete is True`.
- `MET` is invalid when all linked evidence items are `RELATED`.
- Criterion provenance must reach a `REQUIREMENT_SOURCE`.
- Evidence provenance must reach an `ARTIFACT`.
- `SPECIFIC_ARTIFACTS` rejects evidence from artifact documents not listed in `artifact_scope.document_ids`.

- [ ] **Step 5: Implement acyclic expression-reference validation**

Use depth-first traversal with `visiting` and `visited` sets. Emit `EXPRESSION_CYCLE` with the cycle path in the message. Typed expression members must resolve to the correct index according to `kind`.

- [ ] **Step 6: Implement public functions**

`validate_report()`:
1. return schema issues immediately if structural errors make safe cross-field inspection impossible;
2. otherwise append deterministic invariant issues in stable path/code order.

`assert_valid_report()` calls `validate_report()` and raises one `ValueError` containing newline-separated `[CODE] path: message` entries when issues exist.

- [ ] **Step 7: Verify green**

```bash
uv run pytest tests/contract/test_schema.py tests/contract/test_validate.py -v
uv run ruff check src/check_validation tests/contract
```

Expected: pass.

- [ ] **Step 8: Commit**

```bash
git add src/check_validation tests/contract/test_validate.py
git commit -m "feat: enforce CHECK report invariants"
```

---

### Task 3: Expression Derivation and Reproducible Scoring

**Files:**
- Create: `src/check_validation/expressions.py`
- Create: `src/check_validation/scoring.py`
- Create: `tests/contract/test_expressions.py`
- Create: `tests/contract/test_scoring.py`
- Modify: `src/check_validation/validate.py`
- Modify: `src/check_validation/__init__.py`

**Interfaces:**
- Produces: `derive_expression_results(report: Mapping[str, Any]) -> list[dict[str, Any]]`
- Produces: `compute_score_summary(report: Mapping[str, Any], *, min_evaluable_ratio: float) -> dict[str, Any]`
- Produces: `score_issues(report: Mapping[str, Any]) -> tuple[ValidationIssue, ...]`

Root expressions are expressions not referenced by another expression. Every simple obligation is represented by a `SINGLE` root expression.

- [ ] **Step 1: Write failing expression tests**

Create four fixture helpers in `test_expressions.py` by deep-copying `minimal_report` and adding the required criteria/assessments. Tests must prove:

```python
def test_any_of_is_met_when_one_alternative_is_met(any_of_report):
    result = derive_expression_results(any_of_report)[0]
    assert result["verdict"] == "MET"


def test_any_of_missing_alternative_does_not_reduce_met(any_of_report):
    verdicts = {
        assessment["criterion_id"]: assessment["verdict"]
        for assessment in any_of_report["assessments"]
    }
    assert set(verdicts.values()) == {"MET", "MISSING"}
    assert derive_expression_results(any_of_report)[0]["verdict"] == "MET"


def test_all_of_met_plus_missing_is_partial(all_of_report):
    assert derive_expression_results(all_of_report)[0]["verdict"] == "PARTIAL"


def test_at_least_two_with_one_met_one_unknown_one_missing_is_unverifiable(
    at_least_two_report,
):
    assert derive_expression_results(at_least_two_report)[0]["verdict"] == "UNVERIFIABLE"
```

Also add `test_nested_any_of_inside_all_of_is_evaluated_recursively` for `(A OR B) AND C`.

- [ ] **Step 2: Run and verify red**

```bash
uv run pytest tests/contract/test_expressions.py -v
```

Expected: import failure for `check_validation.expressions`.

- [ ] **Step 3: Implement expression combination rules**

After removing `DOES_NOT_APPLY` criterion members from active logical evaluation and treating `APPLICABILITY_UNKNOWN` as unresolved:

```python
def _combine(operator: str, verdicts: list[str], minimum_satisfied: int | None) -> str:
    if operator == "SINGLE":
        return verdicts[0]

    if operator == "ALL_OF":
        if all(verdict == "MET" for verdict in verdicts):
            return "MET"
        if any(verdict == "CONTRADICTED" for verdict in verdicts):
            return "CONTRADICTED"
        if any(verdict in {"MET", "PARTIAL"} for verdict in verdicts):
            return "PARTIAL"
        if any(verdict == "MISSING" for verdict in verdicts):
            return "MISSING"
        return "UNVERIFIABLE"

    if operator == "ANY_OF":
        if any(verdict == "MET" for verdict in verdicts):
            return "MET"
        if any(verdict == "PARTIAL" for verdict in verdicts):
            return "PARTIAL"
        if any(verdict == "UNVERIFIABLE" for verdict in verdicts):
            return "UNVERIFIABLE"
        if verdicts and all(verdict == "CONTRADICTED" for verdict in verdicts):
            return "CONTRADICTED"
        return "MISSING"

    if operator == "AT_LEAST_N_OF":
        if minimum_satisfied is None:
            raise ValueError("AT_LEAST_N_OF requires minimum_satisfied")
        met = verdicts.count("MET")
        partial = verdicts.count("PARTIAL")
        unknown = verdicts.count("UNVERIFIABLE")
        if met >= minimum_satisfied:
            return "MET"
        if met + partial >= minimum_satisfied:
            return "PARTIAL"
        if met + partial + unknown >= minimum_satisfied:
            return "UNVERIFIABLE"
        deficit_verdicts = [
            verdict for verdict in verdicts if verdict not in {"MET", "PARTIAL"}
        ]
        if deficit_verdicts and all(
            verdict == "CONTRADICTED" for verdict in deficit_verdicts
        ):
            return "CONTRADICTED"
        return "MISSING"

    raise ValueError(f"Unsupported expression operator: {operator}")
```

If all members are `DOES_NOT_APPLY`, return an expression result with `verdict: "UNVERIFIABLE"` and `excluded_reason: "DOES_NOT_APPLY"`. If an unresolved source conflict governs the expression, return `UNVERIFIABLE` with `excluded_reason: "SOURCE_CONFLICT"`. Do not score either case.

- [ ] **Step 4: Write failing scoring tests**

Add a local helper that replaces the minimal report's single root unit with any list of already-derived root results:

```python
def set_root_results(report: dict, results: list[dict]) -> dict:
    report["expression_results"] = results
    return report
```

Write these exact assertions:

```python
def test_met_scores_one(minimal_report):
    summary = compute_score_summary(minimal_report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] == 1.0


def test_partial_scores_half(minimal_report):
    minimal_report["expression_results"][0]["verdict"] = "PARTIAL"
    summary = compute_score_summary(minimal_report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] == 0.5


def test_unverifiable_is_excluded(minimal_report):
    minimal_report["expression_results"][0]["verdict"] = "UNVERIFIABLE"
    summary = compute_score_summary(minimal_report, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] is None
    assert summary["excluded_counts"]["unverifiable"] == 1


def test_low_evaluability_suppresses_percentage(five_unit_report):
    summary = compute_score_summary(five_unit_report, min_evaluable_ratio=0.60)
    assert summary["evaluability"]["required"] == "INSUFFICIENT"
    assert summary["required_coverage"] is None
```

`five_unit_report` contains one `MET` required root expression and four `UNVERIFIABLE` required root expressions, so its required evaluable ratio is exactly `0.20`.

- [ ] **Step 5: Implement scoring**

Use:

```python
VERDICT_WEIGHT = {
    "MET": 1.0,
    "PARTIAL": 0.5,
    "MISSING": 0.0,
    "CONTRADICTED": 0.0,
}
```

Rules:
- score root expressions only;
- required and preferred are separate;
- `UNVERIFIABLE`, `DOES_NOT_APPLY`, `APPLICABILITY_UNKNOWN`, unresolved `SOURCE_CONFLICT`, and `UNSPECIFIED` are excluded;
- record `threshold_used`;
- mark each group `SUFFICIENT` only when `scoreable / applicable >= min_evaluable_ratio`;
- when a group is insufficient, set that coverage to `None` and write a concrete suppression reason containing scoreable/applicable counts.

- [ ] **Step 6: Validate expression results and score summary**

`score_issues(report)` reads `report["score_summary"]["threshold_used"]`, recomputes expression results and score summary, and emits:

```text
EXPRESSION_RESULT_MISMATCH
SCORE_SUMMARY_MISMATCH
```

Do not compare free-text `reasoning`; compare IDs, verdicts, score strengths, exclusion reasons, counts, coverage values, evaluability, and threshold.

Extend `validate_report()` to append `score_issues()` after structural/cross-field checks pass.

- [ ] **Step 7: Verify green**

```bash
uv run pytest tests/contract/test_expressions.py tests/contract/test_scoring.py tests/contract/test_validate.py -v
uv run ruff check src/check_validation tests/contract
```

Expected: pass.

- [ ] **Step 8: Commit**

```bash
git add src/check_validation tests/contract
git commit -m "feat: add CHECK expression and scoring semantics"
```

---

### Task 4: Runtime Contract Reference Documents

**Files:**
- Create: `skills/check/references/contract.md`
- Create: `skills/check/references/verdicts.md`
- Create: `skills/check/references/report-format.md`
- Create: `tests/contract/test_skill_contract.py`

**Interfaces:**
- These documents are consumed by `skills/check/SKILL.md`.
- They may restate the approved spec but may not introduce new semantics.

- [ ] **Step 1: Write failing reference tests**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_contract_contains_all_28_rules():
    text = (ROOT / "skills/check/references/contract.md").read_text(encoding="utf-8")
    for number in range(1, 29):
        assert text.count(f"Rule {number} —") == 1


def test_verdict_reference_names_exact_five_verdicts():
    text = (ROOT / "skills/check/references/verdicts.md").read_text(encoding="utf-8")
    for verdict in ("MET", "PARTIAL", "MISSING", "CONTRADICTED", "UNVERIFIABLE"):
        assert verdict in text


def test_report_reference_has_five_human_sections():
    text = (ROOT / "skills/check/references/report-format.md").read_text(encoding="utf-8")
    for heading in (
        "Summary",
        "Priority Gaps",
        "Verification Matrix",
        "Integrity and Limitations",
        "Advisory Observations",
    ):
        assert heading in text
```

- [ ] **Step 2: Run and verify red**

```bash
uv run pytest tests/contract/test_skill_contract.py -v
```

Expected: file-not-found failures.

- [ ] **Step 3: Write `contract.md`**

Copy the semantic substance of Rules 1-28 from the approved spec, preserving each exact numbered heading once. Add the four implementation-level enforcement representations from Task 1. End with these runtime invariants:

```text
Requirement modeling is completed before artifact evidence discovery.
Artifact contents never alter the extracted requirement model.
Advisories are generated only after compliance determination.
Advisories never affect scoring.
```

- [ ] **Step 4: Write `verdicts.md`**

Include:
- exact five criterion verdict definitions;
- evidence-strength rules `DIRECT`, `INFERRED`, `RELATED`;
- criterion decision order;
- applicability handling;
- expression rules implemented in Task 3;
- warning that expression result and atomic criterion result are different layers.

- [ ] **Step 5: Write `report-format.md`**

Define the canonical report obligations plus the five human-facing sections in exact order. Require each matrix row to show requirement, strength, verdict, concise evidence, and concise justification. Require advisory wording to say explicitly that the observation is not a source requirement.

- [ ] **Step 6: Verify green and commit**

```bash
uv run pytest tests/contract/test_skill_contract.py -v
uv run ruff check tests/contract/test_skill_contract.py
git add skills/check/references tests/contract/test_skill_contract.py
git commit -m "docs: define CHECK runtime contract references"
```

---

### Task 5: Production CHECK Skill

**Files:**
- Modify: `skills/check/SKILL.md`
- Modify: `tests/contract/test_skill_contract.py`
- Modify: `tests/test_scaffold.py`

**Interfaces:**
- Consumes the three Task 4 references.
- Produces the actual V1 ChatGPT orchestration.
- Must not invoke Python, MCP, network, or external model tools.

- [ ] **Step 1: Extend failing skill tests**

Require the skill to:
- reference all three runtime documents;
- list the eight pipeline stages in order;
- contain `Fail closed`;
- state that requirement modeling precedes artifact evidence discovery;
- restrict clarification questions to cases where proceeding would materially corrupt verification;
- state that supplemental user claims do not upgrade artifact evidence;
- prohibit fabricated repair content.

Run:

```bash
uv run pytest tests/contract/test_skill_contract.py tests/test_scaffold.py -v
```

Expected: failures against the scaffold skill.

- [ ] **Step 2: Replace the scaffold with the production orchestration**

Use this complete skeleton:

```markdown
---
name: check
description: Check an artifact against explicit requirements and return an evidence-grounded compliance report.
---

# CHECK

Use CHECK when the user wants to compare a designated artifact or artifact set against an explicit requirement source or source set.

Read before evaluating:
- `references/contract.md`
- `references/verdicts.md`
- `references/report-format.md`

## Non-negotiable boundary

Requirements come only from designated requirement sources. Never move the goalposts. Never treat supplemental user claims as artifact evidence. Never claim external truth beyond what supplied evidence establishes.

## Pipeline

1. Classify inputs.
2. Assess extraction quality and limitations.
3. Model requirements independently of artifact evidence.
4. Discover evidence in the designated artifact scope.
5. Assess atomic criteria and logical expressions.
6. Perform artifact-integrity analysis and reassess affected outcomes.
7. Derive reproducible scores and separate non-scoring advisories.
8. Validate the report contract and render the human-facing result.

## Fail closed

When material input cannot be read or a criterion cannot be evaluated reliably, preserve what can be established and mark affected outcomes `UNVERIFIABLE` or excluded rather than guessing.

## Clarification policy

Ask only when proceeding would materially corrupt verification: unresolved input roles, blocking source precedence, or a requested conditional evaluation that cannot safely remain unresolved. Otherwise report ambiguity, absence, conflict, or unverifiability directly.

## Repair boundary

For `PARTIAL`, `MISSING`, or `CONTRADICTED`, explain what genuine evidence or artifact change would resolve the gap. Never invent qualifications, dates, experience, claims, citations, or compliance.
```

- [ ] **Step 3: Verify skill behavior contract**

```bash
uv run pytest tests/contract/test_skill_contract.py tests/test_scaffold.py -v
uv run pytest -q
uv run ruff check .
```

Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add skills/check/SKILL.md tests/contract/test_skill_contract.py tests/test_scaffold.py
git commit -m "feat: implement CHECK V1 skill workflow"
```

---

### Task 6: Cross-Domain and Adversarial Fixture Corpus

**Files:**
- Create: `schemas/fixtures.schema.json`
- Create: `tests/contract/test_fixture_corpus.py`
- Create fixture directories under `tests/fixtures/`
- Create adversarial fixture directories under `tests/adversarial/`

**Interfaces:**
- Every fixture directory contains exactly `requirements.txt`, `artifact.txt`, `expected.json`, and `README.md`.
- `expected.json` is gold semantic expectation metadata, not a generated CHECK report.

- [ ] **Step 1: Write failing corpus tests**

The test must require these seven domain families:

```text
cv-job
essay-rubric
proposal-brief
software-acceptance
report-deliverables
eligibility
policy
```

It must also require these adversarial risk tags:

```text
goalpost-expansion
plausibility-trap
false-absence
overlap-double-counting
ambiguity-invention
documentary-vs-reality
logical-or-corruption
duplicate-requirement-inflation
incomplete-extraction-as-missing
source-conflict
artifact-integrity
conditional-applicability
```

For every fixture, load `expected.json`, validate it with Draft 2020-12, and assert all named files exist.

Run:

```bash
uv run pytest tests/contract/test_fixture_corpus.py -v
```

Expected: missing schema/fixture failures.

- [ ] **Step 2: Implement `fixtures.schema.json`**

Require this top-level shape:

```json
{
  "fixture_id": "cv-job-basic-001",
  "domain": "cv-job",
  "risk_tags": ["requirement-extraction", "verdict"],
  "requirement_source_files": ["requirements.txt"],
  "artifact_files": ["artifact.txt"],
  "supplemental_files": [],
  "expectations": {
    "criteria": [
      {
        "expectation_id": "EXP-001",
        "source_excerpt": "Minimum three years of customer support experience.",
        "normalized_requirement": "3+ years customer support experience",
        "strength": "REQUIRED",
        "verdict": "MET",
        "evidence_excerpt": "Customer Support Engineer — 2021 to 2025"
      }
    ],
    "expressions": [],
    "integrity_findings": [],
    "score_behavior": {
      "required_coverage": 1.0,
      "preferred_coverage": null,
      "score_should_be_withheld": false
    }
  }
}
```

Use canonical requirement-strength and verdict enums. Reject unknown top-level fields.

- [ ] **Step 3: Add seven baseline fixtures**

Create exactly:

```text
cv-job-basic-001
essay-rubric-basic-001
proposal-brief-basic-001
software-acceptance-basic-001
report-deliverables-basic-001
eligibility-basic-001
policy-basic-001
```

Across the seven baselines, include at least one `PREFERRED`, one `CONDITIONAL`, one quantitative threshold, one temporal threshold, and one prohibition.

- [ ] **Step 4: Add focused adversarial fixtures**

Cover all twelve risk tags. Mandatory cases:
- AWS OR Azure with only Azure present => expression `MET`.
- Prohibition with incomplete artifact extraction => `UNVERIFIABLE`.
- Overlapping job dates => overlap diagnostic; no duplicated duration.
- Claimed certification => documentary coverage only; no external-verification claim.
- No Git requirement in source => no Git criterion.
- Two incompatible thresholds without precedence => unresolved source conflict and score exclusion.

- [ ] **Step 5: Verify corpus and commit**

```bash
uv run pytest tests/contract/test_fixture_corpus.py -v
uv run pytest -q
uv run ruff check .
git add schemas/fixtures.schema.json tests/fixtures tests/adversarial tests/contract/test_fixture_corpus.py
git commit -m "test: add CHECK cross-domain fixture corpus"
```

---

### Task 7: End-to-End Evaluation Harness

**Files:**
- Modify: `src/check_validation/models.py`
- Create: `src/check_validation/evaluate.py`
- Create: `tests/eval/test_metrics.py`
- Create: `evals/README.md`
- Create: `evals/cases/README.md`
- Create: `evals/results/.gitkeep`
- Create: `evals/annotations/.gitkeep`
- Create: `evals/release-checklist.md`

**Interfaces:**
- Produces: `EvaluationMetrics`
- Produces: `compute_evaluation_metrics(observations: Sequence[Mapping[str, Any]]) -> EvaluationMetrics`

One observation has this exact shape:

```json
{
  "case_id": "cv-job-basic-001",
  "expectation_id": "EXP-001",
  "expected_verdict": "MET",
  "observed_verdict": "MET",
  "evidence_grounded": true,
  "requirement_overextracted": false,
  "unsupported_assumption": false,
  "logic_preserved": true,
  "report_contract_valid": true,
  "notes": ""
}
```

- [ ] **Step 1: Write failing metric tests**

Primary definitions:

```text
False MET Rate = false observed MET / all observed MET
Unnecessary UNVERIFIABLE Rate = unnecessary observed UNVERIFIABLE / all observed UNVERIFIABLE
```

A false observed MET means `observed_verdict == "MET"` and `expected_verdict != "MET"`.
An unnecessary observed UNVERIFIABLE means `observed_verdict == "UNVERIFIABLE"` and `expected_verdict != "UNVERIFIABLE"`.
If a denominator is zero, the corresponding rate is `None`.

Executable test:

```python
def test_primary_risk_metrics():
    observations = [
        {
            "case_id": "A",
            "expectation_id": "1",
            "expected_verdict": "MISSING",
            "observed_verdict": "MET",
            "evidence_grounded": False,
            "requirement_overextracted": False,
            "unsupported_assumption": True,
            "logic_preserved": True,
            "report_contract_valid": True,
            "notes": "",
        },
        {
            "case_id": "B",
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
            "case_id": "C",
            "expectation_id": "1",
            "expected_verdict": "MET",
            "observed_verdict": "UNVERIFIABLE",
            "evidence_grounded": True,
            "requirement_overextracted": False,
            "unsupported_assumption": False,
            "logic_preserved": True,
            "report_contract_valid": True,
            "notes": "",
        },
    ]
    metrics = compute_evaluation_metrics(observations)
    assert metrics.false_met_rate == 0.5
    assert metrics.unnecessary_unverifiable_rate == 1.0
    assert metrics.unsupported_assumption_count == 1
```

- [ ] **Step 2: Run and verify red**

```bash
uv run pytest tests/eval/test_metrics.py -v
```

Expected: import failure for `check_validation.evaluate`.

- [ ] **Step 3: Implement `EvaluationMetrics` and calculation**

Add exactly:

```python
@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    observations: int
    verdict_accuracy: float | None
    false_met_count: int
    observed_met_count: int
    false_met_rate: float | None
    unnecessary_unverifiable_count: int
    observed_unverifiable_count: int
    unnecessary_unverifiable_rate: float | None
    requirement_overextraction_count: int
    unsupported_assumption_count: int
    logic_corruption_count: int
    report_contract_violation_count: int
```

Reject observations whose verdicts are not one of the five canonical values.

- [ ] **Step 4: Document the end-to-end evaluation workflow**

`evals/README.md` must instruct the evaluator to:
1. open the current CHECK build in ChatGPT testing;
2. run one natural-language fixture invocation;
3. save the canonical report under `evals/results/{run_id}/{case_id}.json`;
4. run `assert_valid_report(report)` on the saved report;
5. manually map observed rows to fixture expectation IDs using source excerpts/provenance rather than generated IDs;
6. save JSONL observations under `evals/annotations/{run_id}.jsonl`;
7. compute the metrics;
8. manually inspect every false `MET`, logic corruption, unsupported assumption, and contract violation.

- [ ] **Step 5: Document threshold selection**

`evals/release-checklist.md` must state that `min_evaluable_ratio` has no production default until baseline end-to-end evidence exists. A release record must name the chosen threshold and empirical justification before production release. Tests may use explicit values such as `0.60`; those are test inputs, not product defaults.

- [ ] **Step 6: Verify and commit**

```bash
uv run pytest tests/eval/test_metrics.py -v
uv run pytest -q
uv run ruff check .
git add src/check_validation/models.py src/check_validation/evaluate.py tests/eval evals
git commit -m "feat: add CHECK semantic evaluation harness"
```

---

### Task 8: Integration, Documentation, and Deterministic V1 Core Gate

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture/README.md`
- Modify: `tests/test_scaffold.py`
- Create: `tests/integration/test_repository_contract.py`

**Interfaces:** No new semantic interfaces. This task proves repository components agree on one contract.

- [ ] **Step 1: Write failing integration tests**

Require:
- `.codex-plugin/plugin.json` keeps `name == "check"`, `version == "0.1.0"`, and `skills == "./skills/"`;
- production skill and all three references exist;
- both JSON schemas exist;
- `CONTRACT_VERSION == "1.0"` matches the spec and minimal report;
- README does not contain `Pre-design scaffold`;
- architecture README states Python is offline-only and the skill has no MCP/runtime dependency;
- every fixture validates;
- `src/check_validation/` imports no `openai`, `agents`, `requests`, `httpx`, `anthropic`, or `google.generativeai`.

Run:

```bash
uv run pytest tests/integration/test_repository_contract.py -v
```

Expected: README/architecture assertions fail before documentation updates.

- [ ] **Step 2: Update README and architecture documentation**

README must document:
- what CHECK does;
- five verdicts;
- compliance versus advisory boundary;
- skills-first/no-persistence boundary;
- repository layout;
- local verification commands;
- evaluation philosophy;
- explicit statement that MCP/UI are deferred until V1 core is production-ready.

Architecture README must show:

```text
ChatGPT
  -> CHECK skill
  -> canonical CheckReport

Offline engineering only
  -> JSON Schema validation
  -> cross-field invariant validation
  -> expression/scoring verification
  -> fixtures and evaluation metrics
```

Do not claim external verification of qualifications, identity, certification validity, legal compliance, or real-world truth.

- [ ] **Step 3: Tighten scaffold tests**

Keep scaffold tests focused on package existence/manifest validity. Add existence assertions for the three runtime reference files. Do not duplicate semantic tests.

- [ ] **Step 4: Run the complete deterministic gate**

PowerShell 7:

```powershell
uv sync --dev
uv run pytest -q
uv run ruff check .
python -m json.tool .codex-plugin/plugin.json *> $null
python -m json.tool schemas/check-report.schema.json *> $null
python -m json.tool schemas/fixtures.schema.json *> $null
git status --short
```

Expected:
- sync succeeds;
- all tests pass;
- Ruff clean;
- all JSON files parse;
- only intentional Task 8 changes appear before commit.

- [ ] **Step 5: Commit integration changes**

```bash
git add README.md docs/architecture/README.md tests/integration tests/test_scaffold.py
git commit -m "docs: finalize CHECK V1 core integration"
```

- [ ] **Step 6: Re-run from a clean tree**

```powershell
uv sync --dev
uv run pytest -q
uv run ruff check .
git status --short
```

Expected: tests pass, Ruff clean, and `git status --short` prints nothing.

- [ ] **Step 7: Human acceptance checkpoint**

Review the production skill, canonical schema, representative validator errors, expression/scoring tests, and representative cross-domain/adversarial fixtures. This checkpoint may approve the deterministic V1 core for end-to-end ChatGPT evaluation, but must not yet call the plugin production-ready. Production readiness requires the end-to-end evaluation procedure and release threshold decision documented in Task 7.

---

## Plan Self-Review

### Spec coverage

- Rules 1-8: schema vocabulary, runtime contract, cross-field validation, source-conflict fixtures.
- Rules 9-11: expression/scoring engine and aggregation fixtures.
- Rules 12-16: integrity schema, provenance checks, uncertainty/evidence invariants, adversarial cases.
- Rules 17-24: artifact scope, input roles, scope/duplication fixtures, report references, skill behavior.
- Rules 25-28: nested expression graph, quantitative/temporal fixtures, complete search scope for absence, documentary-vs-reality fixture.
- Ten canonical domain objects and embedded records: Task 1 schema.
- Eight-stage pipeline: Tasks 4-5.
- Four testing layers: Tasks 1-7.
- Cross-domain corpus: Task 6.
- False MET and Unnecessary UNVERIFIABLE metrics: Task 7.
- No-server/no-UI/no-persistence V1 boundary: global constraints and Task 8 integration checks.

### Public Python interface consistency

```python
schema_issues(report, path=None) -> tuple[ValidationIssue, ...]
validate_report(report, schema_path=None) -> tuple[ValidationIssue, ...]
assert_valid_report(report, schema_path=None) -> None
derive_expression_results(report) -> list[dict[str, Any]]
compute_score_summary(report, *, min_evaluable_ratio: float) -> dict[str, Any]
score_issues(report) -> tuple[ValidationIssue, ...]
compute_evaluation_metrics(observations) -> EvaluationMetrics
```

### Scope

This plan implements the CHECK V1 verification core only. OpenAI public-directory submission/deployment and any future MCP/UI work are separate plans because they introduce distinct infrastructure, review, and acceptance gates.
