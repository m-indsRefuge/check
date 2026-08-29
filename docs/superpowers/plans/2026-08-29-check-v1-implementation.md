# CHECK V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build CHECK V1 as a skills-first ChatGPT plugin with a canonical report schema, deterministic offline validation and scoring, a production CHECK skill, and a cross-domain evaluation corpus that enforces the approved 28-rule verification contract.

**Architecture:** ChatGPT performs semantic requirement extraction, evidence discovery, and assessment through `skills/check/SKILL.md`. The repository defines the authoritative `CheckReport` boundary in JSON Schema and a small Python validation package that enforces only deterministic structural and scoring invariants; it must not reproduce semantic model reasoning. Cross-domain fixtures and an evaluation harness measure semantic behavior, with False MET Rate and Unnecessary UNVERIFIABLE Rate as primary risk metrics.

**Tech Stack:** Python >=3.12, JSON Schema Draft 2020-12, `jsonschema` 4.x, pytest 9.x, Ruff 0.16+, OpenAI skill/plugin package layout.

**Spec:** `docs/superpowers/specs/2026-08-29-check-v1-design.md`

## Global Constraints

- Contract version is exactly `1.0` for this implementation.
- V1 is skills-first and must function in ChatGPT without an MCP server or Python runtime dependency.
- Do not add an API service, database, authentication, persistent document storage, React UI, custom widget, embeddings/vector store, external model calls, proprietary model, domain-specific CV engine, or user-configurable rule engine.
- The Python package is offline engineering-assurance infrastructure only.
- The canonical schema is authoritative for report structure; Python may add cross-field validation but may not redefine semantic verdict meaning.
- Semantic uncertainty is represented with contract states such as `AMBIGUOUS`, `UNVERIFIABLE`, `APPLICABILITY_UNKNOWN`, and extraction limitations; do not add arbitrary numeric model-confidence scores.
- Do not store or expose model chain-of-thought. Human-readable `reasoning` is a concise auditable justification only.
- Requirements must be modeled independently of artifact contents before evidence discovery begins.
- Advisories never affect compliance verdicts or scores.
- Compound logical obligations are scored once at the top-level expression result; atomic alternatives are never independently double-counted.
- `MET` requires evidence; `PARTIAL` requires evidence; `CONTRADICTED` requires conflicting evidence; `UNVERIFIABLE` requires a limiting condition; `MISSING` requires a complete documented search scope.
- Negative/absence requirements may be `MET` only when the relevant artifact scope was completely inspected.
- False `MET` is release-critical. Excessive `UNVERIFIABLE` is also tracked to prevent a uselessly conservative checker.
- Repository text stays LF-normalized under the existing `.gitattributes` policy.

## File Structure

The implementation converges on this structure:

```text
check/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── check/
│       ├── SKILL.md
│       └── references/
│           ├── contract.md
│           ├── verdicts.md
│           └── report-format.md
├── schemas/
│   ├── check-report.schema.json
│   └── fixtures.schema.json
├── src/
│   └── check_validation/
│       ├── __init__.py
│       ├── models.py
│       ├── schema.py
│       ├── validate.py
│       ├── expressions.py
│       ├── scoring.py
│       └── evaluate.py
├── tests/
│   ├── contract/
│   │   ├── conftest.py
│   │   ├── test_schema.py
│   │   ├── test_validate.py
│   │   ├── test_expressions.py
│   │   ├── test_scoring.py
│   │   └── test_skill_contract.py
│   ├── fixtures/
│   │   ├── cv-job/
│   │   ├── essay-rubric/
│   │   ├── proposal-brief/
│   │   ├── software-acceptance/
│   │   ├── report-deliverables/
│   │   ├── eligibility/
│   │   └── policy/
│   ├── adversarial/
│   ├── eval/
│   │   └── test_metrics.py
│   ├── integration/
│   │   └── test_repository_contract.py
│   └── test_scaffold.py
├── evals/
│   ├── cases/
│   ├── results/
│   │   └── .gitkeep
│   ├── annotations/
│   │   └── .gitkeep
│   ├── README.md
│   └── release-checklist.md
├── docs/
│   ├── architecture/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── pyproject.toml
└── README.md
```

### File responsibilities

- `schemas/check-report.schema.json`: authoritative canonical report structure and enum vocabulary.
- `schemas/fixtures.schema.json`: format for semantic/adversarial fixture metadata and expected outcomes.
- `models.py`: deterministic Python enums and `ValidationIssue` / evaluation metric records only; no semantic decision engine.
- `schema.py`: load and run Draft 2020-12 JSON Schema validation.
- `validate.py`: enforce cross-field invariants that JSON Schema cannot express safely.
- `expressions.py`: derive `SINGLE`, `ALL_OF`, `ANY_OF`, and `AT_LEAST_N_OF` expression results from already-produced criterion assessments.
- `scoring.py`: calculate reproducible Required/Preferred coverage from authoritative assessment/expression results.
- `evaluate.py`: compare manually annotated end-to-end observations and compute semantic-risk metrics.
- skill reference files: authoritative runtime guidance distilled from the approved spec.
- `SKILL.md`: short orchestration instructions; it references the deeper documents instead of duplicating them.

---

### Task 1: Canonical Schema and Validation Foundation

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
- Later tasks consume the canonical field/enumeration names defined here.

**Implementation clarification to record in the spec before schema code:** the approved rules require three enforcement fields that were implicit but not enumerated in the original object field lists. Add them without changing contract semantics:

1. `Criterion.artifact_scope` to enforce Rule 21 cross-artifact boundaries.
2. `CriterionAssessment.search_scope` to prove complete search for `MISSING` and proof-of-absence outcomes under Rules 3 and 27.
3. `RequirementExpression.members` becomes explicit typed references that may point to either a criterion or another expression, allowing nested logic such as `(A OR B) AND C` while preserving Rule 25.

Use these exact embedded shapes:

```json
{
  "artifact_scope": {
    "mode": "ALL_ARTIFACTS",
    "document_ids": []
  },
  "search_scope": {
    "document_ids": ["DOC-2"],
    "locations": ["Employment History", "Skills"],
    "complete": true,
    "notes": []
  },
  "expression_member": {
    "kind": "CRITERION",
    "id": "REQ-001"
  }
}
```

`artifact_scope.mode` is exactly `ALL_ARTIFACTS` or `SPECIFIC_ARTIFACTS`; `SPECIFIC_ARTIFACTS` requires at least one `document_id`. `SourceSpan.location` is optional because the contract already says location is retained only when reliably available.

- [ ] **Step 1: Add failing schema tests and a reusable minimal report builder**

Create `tests/contract/conftest.py` with a `minimal_valid_report()` helper returning a complete report containing one requirement source, one artifact, one requirement span, one artifact span, one `REQUIRED` criterion, one `SINGLE` expression, one `DIRECT` evidence item, one `MET` assessment, one expression result, and a 100% required score summary.

The helper must use these IDs consistently:

```python
REPORT_ID = "REPORT-001"
REQ_DOC = "DOC-REQ"
ART_DOC = "DOC-ART"
REQ_SPAN = "SPAN-REQ-001"
ART_SPAN = "SPAN-ART-001"
CRITERION = "REQ-001"
EXPRESSION = "EXPR-001"
EVIDENCE = "EVID-001"
ASSESSMENT = "ASSESS-001"
```

Create `tests/contract/test_schema.py` with at least these tests:

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

Run:

```bash
uv run pytest tests/contract/test_schema.py -v
```

Expected: collection/import failure because `check_validation.schema` and the canonical schema do not yet exist.

- [ ] **Step 3: Add offline validation dependencies and source import path**

Modify `pyproject.toml` to retain `requires-python = ">=3.12"` and add:

```toml
dependencies = [
    "jsonschema>=4.23,<5",
]

[dependency-groups]
dev = [
    "pytest>=9,<10",
    "ruff>=0.16,<1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

Keep `[tool.uv] package = false` so the skill remains the runtime product and the Python source remains repository tooling.

Run:

```bash
uv sync --dev
```

Expected: successful environment resolution.

- [ ] **Step 4: Record the three enforcement-field clarifications in the approved spec**

Update the domain-model field lists and explanatory text only. Do not alter any verdict, scoring, evidence, or user-facing semantics. The spec must explicitly say nested expressions form an acyclic expression graph/tree and that cross-field validation rejects cycles.

- [ ] **Step 5: Implement the canonical report schema**

Use JSON Schema Draft 2020-12:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://check.invalid/schemas/check-report.schema.json",
  "title": "CHECK V1 CheckReport",
  "type": "object",
  "additionalProperties": false,
  "required": [
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
}
```

Define every canonical object and embedded record under `$defs`. Use these exact enum vocabularies:

```text
InputRole: REQUIREMENT_SOURCE | ARTIFACT | SUPPLEMENTAL_CONTEXT
ContentStatus: AVAILABLE | PARTIAL | UNREADABLE | UNAVAILABLE
ExtractionQuality: COMPLETE | DEGRADED | UNKNOWN
RequirementStrength: REQUIRED | PREFERRED | CONDITIONAL | UNSPECIFIED
EffectiveStrength: REQUIRED | PREFERRED | UNSPECIFIED
InterpretationState: CLEAR | AMBIGUOUS
Applicability: APPLIES | DOES_NOT_APPLY | APPLICABILITY_UNKNOWN | NOT_CONDITIONAL
RequirementKind: PRESENCE | ABSENCE | QUANTITATIVE | QUALITATIVE | TEMPORAL | OTHER
ExpressionOperator: SINGLE | ALL_OF | ANY_OF | AT_LEAST_N_OF
ExpressionMemberKind: CRITERION | EXPRESSION
EvidenceStrength: DIRECT | INFERRED | RELATED
Verdict: MET | PARTIAL | MISSING | CONTRADICTED | UNVERIFIABLE
AggregationStatus: AGGREGATION_OK | OVERLAP_DETECTED | AGGREGATION_AMBIGUOUS | AGGREGATION_CONFLICT
IntegritySeverity: INFO | WARNING | ERROR
IntegrityCategory: CONTRADICTORY_FACTS | IMPOSSIBLE_VALUE | DUPLICATE_CONFLICT | TEMPORAL_CONFLICT | AGGREGATION_CONFLICT | OTHER
IntegrityImpact: NO_VERDICT_IMPACT | LIMITS_VERIFICATION | INVALIDATES_EVIDENCE
Evaluability: SUFFICIENT | INSUFFICIENT
ArtifactScopeMode: ALL_ARTIFACTS | SPECIFIC_ARTIFACTS
```

The top-level `source_spans` array is required because both criteria and evidence reference span IDs and the report must remain self-contained.

- [ ] **Step 6: Implement Python schema helpers**

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

`schema.py` must use `jsonschema.Draft202012Validator`, sort errors by path, and convert each error to `ValidationIssue(code="SCHEMA", path=<json-pointer-like-path>, message=error.message)`.

- [ ] **Step 7: Run focused tests and lint**

Run:

```bash
uv run pytest tests/contract/test_schema.py -v
uv run ruff check src/check_validation tests/contract/test_schema.py tests/contract/conftest.py
```

Expected: all focused tests pass and Ruff reports no errors.

- [ ] **Step 8: Commit Task 1**

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
- Consumes: `schema_issues()` and `ValidationIssue` from Task 1.
- Produces: `validate_report(report: Mapping[str, Any], schema_path: Path | None = None) -> tuple[ValidationIssue, ...]`
- Produces: `assert_valid_report(report: Mapping[str, Any], schema_path: Path | None = None) -> None`
- `assert_valid_report` raises `ValueError` containing newline-separated `[CODE] path: message` entries when any issue exists.

- [ ] **Step 1: Write failing invariant tests**

Create tests for these exact invariant codes:

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
REFERENCE_NOT_FOUND
EXPRESSION_CYCLE
ARTIFACT_SCOPE_VIOLATION
ADVISORY_MUST_NOT_BE_SCOREABLE
```

Representative tests:

```python
def test_met_without_evidence_is_invalid(minimal_report):
    minimal_report["assessments"][0]["evidence_ids"] = []
    issues = validate_report(minimal_report)
    assert "MET_REQUIRES_EVIDENCE" in {issue.code for issue in issues}


def test_missing_requires_complete_search_scope(minimal_report):
    assessment = minimal_report["assessments"][0]
    assessment["verdict"] = "MISSING"
    assessment["evidence_ids"] = []
    assessment["search_scope"] = {
        "document_ids": ["DOC-ART"],
        "locations": ["Skills"],
        "complete": False,
        "notes": ["Second page unavailable"],
    }
    issues = validate_report(minimal_report)
    assert "MISSING_REQUIRES_COMPLETE_SEARCH_SCOPE" in {i.code for i in issues}


def test_related_evidence_alone_cannot_support_met(minimal_report):
    minimal_report["evidence"][0]["strength"] = "RELATED"
    issues = validate_report(minimal_report)
    assert "RELATED_CANNOT_SOLELY_SUPPORT_MET" in {i.code for i in issues}
```

Also test a nested expression cycle `EXPR-A -> EXPR-B -> EXPR-A` and an evidence item sourced from `DOC-OTHER` when the criterion's artifact scope permits only `DOC-ART`.

- [ ] **Step 2: Run focused tests and verify red**

```bash
uv run pytest tests/contract/test_validate.py -v
```

Expected: import failure because `validate.py` does not exist.

- [ ] **Step 3: Implement deterministic indices and reference validation**

In `validate.py`, build dictionaries keyed by document, span, criterion, expression, evidence, and assessment ID. Add duplicate-ID detection under code `DUPLICATE_ID`. Validate every referenced ID before running semantic cross-field checks so later checks never dereference unknown objects.

Use a private helper with this signature:

```python
def _index_by_id(items: Sequence[Mapping[str, Any]], key: str) -> tuple[dict[str, Mapping[str, Any]], list[ValidationIssue]]:
    ...
```

- [ ] **Step 4: Implement verdict/evidence invariants**

Implement the exact rules from the tests. `UNVERIFIABLE` is valid only when `uncertainty_notes` is non-empty or a report/input limitation is explicitly linked by ID if the schema later adds limitation references. For V1, require non-empty `uncertainty_notes` directly on the assessment.

`MISSING` requires `search_scope.complete is True`. `ABSENCE` + `MET` also requires `search_scope.complete is True`.

`MET` may use one or more `DIRECT`/`INFERRED` evidence items. It is invalid when every linked evidence item is only `RELATED`.

- [ ] **Step 5: Implement provenance, artifact-scope, and expression-graph checks**

- Criterion `original_spans` must reference at least one span belonging to a `REQUIREMENT_SOURCE` document.
- Evidence `source_spans` must reference at least one span belonging to an `ARTIFACT` document.
- For `SPECIFIC_ARTIFACTS`, every evidence source document used for the criterion must be listed in `artifact_scope.document_ids`.
- Nested expression references must resolve.
- Expression graph must be acyclic; detect cycles with depth-first traversal and emit one `EXPRESSION_CYCLE` issue per encountered cycle path.

- [ ] **Step 6: Implement public validation functions**

`validate_report()` must return schema issues first, then deterministic cross-field issues. If schema issues make a section structurally unusable, skip dependent cross-field checks rather than throwing.

`assert_valid_report()` must be a thin wrapper over `validate_report()`.

- [ ] **Step 7: Run Task 2 and regression gates**

```bash
uv run pytest tests/contract/test_schema.py tests/contract/test_validate.py -v
uv run ruff check src/check_validation tests/contract
```

Expected: all tests pass.

- [ ] **Step 8: Commit Task 2**

```bash
git add src/check_validation tests/contract/test_validate.py
git commit -m "feat: enforce CHECK report invariants"
```

---

### Task 3: Logical Expression Derivation and Coverage Scoring

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
- Produces: `score_issues(report: Mapping[str, Any], *, min_evaluable_ratio: float) -> tuple[ValidationIssue, ...]`
- Root expressions are expressions not referenced as a member by another expression. Every simple criterion must be represented by a `SINGLE` root expression so scoring has one uniform unit model.

- [ ] **Step 1: Write failing expression-semantics tests**

Cover these exact behaviors:

```python
def test_any_of_is_met_when_one_alternative_is_met(any_of_report):
    result = derive_expression_results(any_of_report)[0]
    assert result["verdict"] == "MET"


def test_any_of_missing_alternative_does_not_create_partial_when_other_is_met(any_of_report):
    # A=MET, B=MISSING => expression MET
    result = derive_expression_results(any_of_report)[0]
    assert result["verdict"] == "MET"


def test_all_of_with_some_real_coverage_is_partial(all_of_report):
    # A=MET, B=MISSING => expression PARTIAL
    result = derive_expression_results(all_of_report)[0]
    assert result["verdict"] == "PARTIAL"


def test_at_least_n_of_is_unverifiable_when_unknown_paths_could_change_outcome(report):
    # need 2; one MET, one UNVERIFIABLE, one MISSING
    result = derive_expression_results(report)[0]
    assert result["verdict"] == "UNVERIFIABLE"
```

Also test nested `(A OR B) AND C` evaluation.

- [ ] **Step 2: Run expression tests and verify red**

```bash
uv run pytest tests/contract/test_expressions.py -v
```

Expected: import failure for `check_validation.expressions`.

- [ ] **Step 3: Implement deterministic expression semantics**

Use these exact rules after recursively resolving child results:

`SINGLE`
- inherit the sole member result.

`ALL_OF`
- all `MET` => `MET`;
- any `CONTRADICTED` => `CONTRADICTED`;
- otherwise, if any `MET` or `PARTIAL` exists => `PARTIAL`;
- otherwise, if any `MISSING` exists => `MISSING`;
- otherwise => `UNVERIFIABLE`.

`ANY_OF`
- any `MET` => `MET`;
- else any `PARTIAL` => `PARTIAL`;
- else any `UNVERIFIABLE` => `UNVERIFIABLE`;
- else if every viable member is `CONTRADICTED` => `CONTRADICTED`;
- else => `MISSING`.

`AT_LEAST_N_OF`
- let `m = count(MET)`, `p = count(PARTIAL)`, `u = count(UNVERIFIABLE)`, required `n`;
- `m >= n` => `MET`;
- `m + p >= n` => `PARTIAL`;
- `m + p + u >= n` => `UNVERIFIABLE`;
- if all remaining deficit paths are `CONTRADICTED` and none are `MISSING` => `CONTRADICTED`;
- otherwise => `MISSING`.

Every derived result contains:

```json
{
  "expression_id": "EXPR-001",
  "verdict": "MET",
  "member_assessment_ids": ["ASSESS-001"],
  "reasoning": "At least one permitted alternative is fully satisfied.",
  "score_strength": "REQUIRED",
  "excluded_reason": null
}
```

For nested expression members, `member_assessment_ids` contains the transitive atomic assessment IDs used to derive the result, deduplicated in stable source order.

- [ ] **Step 4: Write failing scoring tests**

Required tests:

```python
def test_required_coverage_uses_root_expressions_once(report_with_any_of):
    summary = compute_score_summary(report_with_any_of, min_evaluable_ratio=0.60)
    assert summary["required_coverage"] == 1.0
    assert summary["required_counts"]["met"] == 1


def test_partial_scores_half():
    ...  # build one REQUIRED root expression with PARTIAL result
    assert summary["required_coverage"] == 0.5


def test_unverifiable_is_excluded_from_denominator():
    ...  # one MET + one UNVERIFIABLE root expression
    assert summary["required_coverage"] == 1.0
    assert summary["excluded_counts"]["unverifiable"] == 1


def test_low_evaluability_withholds_percentage():
    ...  # one scoreable + four UNVERIFIABLE, threshold 0.60
    assert summary["evaluability"] == "INSUFFICIENT"
    assert summary["required_coverage"] is None
```

The ellipses above are instructions for fixture construction only; do not leave ellipses in committed test code. Build the complete reports using the Task 1 helper.

- [ ] **Step 5: Implement scoring**

Use exact verdict weights:

```python
VERDICT_WEIGHT = {
    "MET": 1.0,
    "PARTIAL": 0.5,
    "MISSING": 0.0,
    "CONTRADICTED": 0.0,
}
```

`UNVERIFIABLE` is excluded. Exclude non-applicable, applicability-unknown, unresolved-source-conflict, and unspecified-strength units. Required and preferred are calculated separately from root expression results.

`compute_score_summary()` must calculate an evaluable ratio separately for required and preferred groups. A group is `SUFFICIENT` only when `scoreable / applicable >= min_evaluable_ratio`. The summary must record `threshold_used` so the result is reproducible. When insufficient, coverage is `None` and `suppression_reason` names the exact counts.

- [ ] **Step 6: Validate report-provided expression results and scores**

Extend `validate.py` so it recomputes expression results and score summary and emits:

```text
EXPRESSION_RESULT_MISMATCH
SCORE_SUMMARY_MISMATCH
```

Do not compare `reasoning` wording byte-for-byte. Compare IDs, verdicts, score strength, exclusions, counts, coverage values, evaluability, and threshold.

- [ ] **Step 7: Run Task 3 gate**

```bash
uv run pytest tests/contract/test_expressions.py tests/contract/test_scoring.py tests/contract/test_validate.py -v
uv run ruff check src/check_validation tests/contract
```

Expected: all tests pass.

- [ ] **Step 8: Commit Task 3**

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
- These files are consumed by `skills/check/SKILL.md` in Task 5.
- They contain runtime instructions only; they never introduce semantics absent from the approved design.

- [ ] **Step 1: Write failing reference-contract tests**

Create tests that assert all three files exist and that the runtime contract includes every numbered rule from `Rule 1` through `Rule 28` exactly once.

```python
def test_contract_reference_contains_all_28_rules(repo_root):
    text = (repo_root / "skills/check/references/contract.md").read_text(encoding="utf-8")
    for number in range(1, 29):
        assert f"Rule {number} —" in text
```

Add tests that `verdicts.md` names exactly the five verdicts and includes the decision order, and that `report-format.md` names the five human-facing sections.

- [ ] **Step 2: Run focused tests and verify red**

```bash
uv run pytest tests/contract/test_skill_contract.py -v
```

Expected: missing-file failures.

- [ ] **Step 3: Write `contract.md`**

Distill the approved 28 rules into concise runtime instructions. Preserve the rule numbers and principle statements. Include the implementation clarifications from Task 1 for artifact scope, search scope, and nested logical expressions.

The document must explicitly state:

```text
Requirement modeling is completed before artifact evidence discovery.
Artifact contents must never change what CHECK decides the requirement source required.
Advisories are generated only after compliance determination and never affect scoring.
```

- [ ] **Step 4: Write `verdicts.md`**

Document the exact five verdict definitions, evidence requirements, evidence-strength rules, applicability behavior, and this decision order:

```text
1. Cannot evaluate reliably -> UNVERIFIABLE
2. Explicit conflicting evidence -> CONTRADICTED
3. Fully satisfied -> MET
4. Meaningful incomplete evidence -> PARTIAL
5. Otherwise, after complete search -> MISSING
```

Include the expression-derivation rules from Task 3 and clearly distinguish criterion verdicts from top-level expression results.

- [ ] **Step 5: Write `report-format.md`**

Specify both canonical report requirements and the human-facing five-section order:

```text
1. Summary
2. Priority Gaps
3. Verification Matrix
4. Integrity and Limitations
5. Advisory Observations
```

Require every matrix row to expose requirement strength, verdict, concise evidence, concise reasoning, and provenance when requested. Require advisory copy to state explicitly when an observation is not a source requirement.

- [ ] **Step 6: Run focused tests and lint**

```bash
uv run pytest tests/contract/test_skill_contract.py -v
uv run ruff check tests/contract/test_skill_contract.py
```

Expected: pass.

- [ ] **Step 7: Commit Task 4**

```bash
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
- Consumes: the three reference documents from Task 4.
- Produces: the actual V1 ChatGPT runtime orchestration instructions.
- The skill does not call Python or an MCP tool.

- [ ] **Step 1: Extend tests for production skill structure**

Add tests requiring:

- YAML frontmatter `name: check` and the existing evidence-grounded description;
- explicit references to `references/contract.md`, `references/verdicts.md`, and `references/report-format.md`;
- all eight processing stages in order;
- a fail-closed instruction;
- a statement that requirements are modeled before artifact inspection for evidence;
- a statement that CHECK asks a clarifying question only when proceeding would materially corrupt verification;
- a statement that repair guidance must not fabricate facts;
- a statement that user supplemental claims do not upgrade artifact evidence.

- [ ] **Step 2: Run focused tests and verify red**

```bash
uv run pytest tests/contract/test_skill_contract.py tests/test_scaffold.py -v
```

Expected: failures because the scaffold skill lacks production instructions.

- [ ] **Step 3: Replace scaffold `SKILL.md` with the production orchestration**

Use this structure and keep the skill concise enough to route detail into references:

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
2. Assess extraction quality.
3. Model requirements independently of artifact evidence.
4. Discover artifact evidence.
5. Assess atomic criteria and logical expressions.
6. Perform artifact-integrity analysis and reassess affected criteria.
7. Derive scores and non-scoring advisories.
8. Validate the report contract, then render the human-facing result.

## Fail closed
When material input cannot be read or a criterion cannot be evaluated reliably, preserve what can be established and mark affected outcomes `UNVERIFIABLE` or excluded rather than guessing.

## Clarification policy
Ask only when proceeding would materially corrupt verification: unresolved input roles, blocking source precedence, or a requested conditional evaluation that cannot safely remain unresolved. Otherwise report ambiguity, absence, or unverifiability directly.

## Repair boundary
For `PARTIAL`, `MISSING`, or `CONTRADICTED`, explain what genuine evidence or artifact change would resolve the gap. Never invent qualifications, dates, experience, claims, citations, or compliance.
```

- [ ] **Step 4: Run skill/scaffold tests**

```bash
uv run pytest tests/contract/test_skill_contract.py tests/test_scaffold.py -v
```

Expected: pass.

- [ ] **Step 5: Run the full deterministic gate so far**

```bash
uv run pytest -q
uv run ruff check .
```

Expected: all tests pass; Ruff clean.

- [ ] **Step 6: Commit Task 5**

```bash
git add skills/check/SKILL.md tests/contract/test_skill_contract.py tests/test_scaffold.py
git commit -m "feat: implement CHECK V1 skill workflow"
```

---

### Task 6: Cross-Domain and Adversarial Fixture Corpus

**Files:**
- Create: `schemas/fixtures.schema.json`
- Create: `tests/contract/test_fixture_corpus.py`
- Create fixture directories/files under `tests/fixtures/` and `tests/adversarial/`

**Interfaces:**
- Every fixture directory contains `requirements.txt`, `artifact.txt`, `expected.json`, and `README.md`.
- `expected.json` validates against `schemas/fixtures.schema.json`.
- Fixtures contain gold semantic expectations, not generated CHECK reports.

Use this exact fixture metadata shape:

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
        "evidence_excerpt": "Support Engineer — 2021 to 2025"
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

- [ ] **Step 1: Write failing corpus-schema tests**

Test that:

- every fixture directory has all four required files;
- every `expected.json` validates against `fixtures.schema.json`;
- the seven required domain families exist;
- adversarial risk tags include every required risk family below.

Required domain families:

```text
cv-job
essay-rubric
proposal-brief
software-acceptance
report-deliverables
eligibility
policy
```

Required adversarial risk families:

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

- [ ] **Step 2: Run corpus tests and verify red**

```bash
uv run pytest tests/contract/test_fixture_corpus.py -v
```

Expected: missing schema/fixture failures.

- [ ] **Step 3: Implement `fixtures.schema.json`**

Use Draft 2020-12, reject unknown top-level fields, require all fields shown above, and constrain `domain`, requirement strength, verdict, and score behavior with the same canonical enums where applicable.

- [ ] **Step 4: Add one baseline fixture for each of the seven domains**

Create these fixture IDs and ensure each has manually obvious ground truth:

```text
cv-job-basic-001
essay-rubric-basic-001
proposal-brief-basic-001
software-acceptance-basic-001
report-deliverables-basic-001
eligibility-basic-001
policy-basic-001
```

At least one baseline fixture must contain `PREFERRED`; at least one must contain `CONDITIONAL`; at least one must contain a quantitative threshold; at least one must contain a prohibition.

- [ ] **Step 5: Add adversarial fixtures covering all twelve risk families**

Use one focused fixture per risk unless two risks naturally belong in the same minimal case. In particular:

- `logical-or-corruption`: AWS OR Azure where exactly Azure is present; top-level obligation must be `MET`.
- `false-absence`: prohibition plus intentionally incomplete artifact content; expected `UNVERIFIABLE`.
- `overlap-double-counting`: overlapping employment dates; expected overlap diagnostic and no duplicate duration.
- `documentary-vs-reality`: artifact states a certification; expected documentary `MET` with no external-verification claim.
- `goalpost-expansion`: source never asks for Git; expected criteria must not include Git.
- `source-conflict`: two explicit incompatible thresholds with no precedence; expected conflict and score exclusion.

- [ ] **Step 6: Run corpus and full deterministic gates**

```bash
uv run pytest tests/contract/test_fixture_corpus.py -v
uv run pytest -q
uv run ruff check .
```

Expected: pass.

- [ ] **Step 7: Commit Task 6**

```bash
git add schemas/fixtures.schema.json tests/fixtures tests/adversarial tests/contract/test_fixture_corpus.py
git commit -m "test: add CHECK cross-domain fixture corpus"
```

---

### Task 7: End-to-End Evaluation Harness and Semantic Risk Metrics

**Files:**
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
- An observation is a manual gold/predicted mapping for one expected criterion or expression after an end-to-end ChatGPT CHECK run.

Use this exact observation shape in `evals/README.md`:

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

Define the primary metrics exactly as:

```text
False MET Rate = observed MET where expected != MET / all observed MET
Unnecessary UNVERIFIABLE Rate = observed UNVERIFIABLE where expected != UNVERIFIABLE / all observed UNVERIFIABLE
```

When a denominator is zero, expose the rate as `None`, not `0.0`.

Tests must also cover:

- verdict accuracy;
- requirement over-extraction count;
- unsupported-assumption count;
- logic-corruption count (`logic_preserved is False`);
- report-contract violation count.

- [ ] **Step 2: Run metric tests and verify red**

```bash
uv run pytest tests/eval/test_metrics.py -v
```

Expected: import failure for `check_validation.evaluate`.

- [ ] **Step 3: Implement `EvaluationMetrics` and metric calculation**

Add to `models.py`:

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

`compute_evaluation_metrics()` must validate verdict strings against the five canonical verdicts and raise `ValueError` for malformed observations instead of silently skipping them.

- [ ] **Step 4: Document the manual end-to-end evaluation procedure**

`evals/README.md` must instruct the evaluator to:

1. install/open the current CHECK plugin/skill build in ChatGPT testing;
2. run the fixture's natural-language invocation with its requirement source and artifact;
3. save the canonical CHECK report returned by the run under `evals/results/<run-id>/<case-id>.json`;
4. validate the report with `assert_valid_report()` using the run's chosen `min_evaluable_ratio`;
5. map observed criteria/expression results to fixture expectation IDs manually, using source excerpts and provenance rather than relying on generated IDs;
6. record observations as JSONL under `evals/annotations/<run-id>.jsonl`;
7. compute metrics with the Python harness;
8. manually inspect every false `MET`, logic corruption, and contract violation before release.

- [ ] **Step 5: Define release-threshold selection procedure without inventing a threshold**

`evals/release-checklist.md` must state that `min_evaluable_ratio` remains a release configuration value until baseline end-to-end runs exist. The release decision records the chosen value plus empirical justification. Do not hard-code a speculative default in the skill or validator.

- [ ] **Step 6: Run Task 7 gate**

```bash
uv run pytest tests/eval/test_metrics.py -v
uv run pytest -q
uv run ruff check .
```

Expected: pass.

- [ ] **Step 7: Commit Task 7**

```bash
git add src/check_validation/models.py src/check_validation/evaluate.py tests/eval evals
git commit -m "feat: add CHECK semantic evaluation harness"
```

---

### Task 8: Repository Integration, Documentation, and Deterministic Release Gate

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture/README.md`
- Modify: `.codex-plugin/plugin.json`
- Create: `tests/integration/test_repository_contract.py`
- Modify: `tests/test_scaffold.py`

**Interfaces:**
- No new semantic interfaces.
- This task verifies that packaging, docs, schema, validator, skill, fixtures, and evaluation assets agree on one V1 contract.

- [ ] **Step 1: Write failing repository-integration tests**

Require:

- plugin manifest still has `name == "check"` and `skills == "./skills/"`;
- manifest version is valid semver and remains `0.1.0` until an explicit release-version task changes it;
- production `SKILL.md` and all three references exist;
- both schemas exist;
- `CONTRACT_VERSION == "1.0"` matches the spec and a minimal canonical report;
- README no longer says `Pre-design scaffold`;
- architecture README describes the skills-first runtime and offline validator boundary;
- every fixture corpus file validates;
- no file under `src/check_validation/` imports an OpenAI/LLM SDK or networking client.

The last assertion can inspect source text for forbidden imports such as `openai`, `agents`, `requests`, `httpx`, `anthropic`, and `google.generativeai`.

- [ ] **Step 2: Run integration test and verify red**

```bash
uv run pytest tests/integration/test_repository_contract.py -v
```

Expected: documentation/status assertions fail before updates.

- [ ] **Step 3: Update public README**

Replace scaffold status with an accurate V1-core status. Document:

- what CHECK does;
- the five verdicts;
- the difference between compliance and advisory observations;
- the skills-first/no-persistence boundary;
- repository layout;
- local engineering commands;
- evaluation philosophy;
- statement that UI/MCP are intentionally out of scope until core V1 is production-ready.

Do not advertise CHECK as externally verifying qualifications, identity, certifications, legal compliance, or real-world truth.

- [ ] **Step 4: Update architecture README**

Document the runtime boundary:

```text
ChatGPT
  -> CHECK skill
  -> canonical CheckReport

Offline engineering only:
  schema validator
  invariant validator
  expression/scoring engine
  fixtures/evaluation harness
```

State explicitly that Python tooling is not called by the skill in V1.

- [ ] **Step 5: Tighten scaffold/package checks**

Update `tests/test_scaffold.py` so it asserts the production skill references exist and the manifest remains valid UTF-8 JSON. Do not duplicate the deeper semantic tests already covered elsewhere.

- [ ] **Step 6: Run the complete deterministic verification gate**

Run exactly:

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
python -m json.tool .codex-plugin/plugin.json > NUL
python -m json.tool schemas/check-report.schema.json > NUL
python -m json.tool schemas/fixtures.schema.json > NUL
```

On non-Windows shells, replace `> NUL` with `> /dev/null`; no repository file should depend on this shell difference.

Expected:

- dependency sync succeeds;
- all tests pass;
- Ruff clean;
- all three JSON files parse successfully.

- [ ] **Step 7: Inspect repository diff for scope violations**

Run:

```bash
git status --short
git diff --stat HEAD~1..HEAD || true
```

Then inspect the complete branch diff against the approved design base. Confirm there is no MCP server, UI, persistence, auth, network call, external LLM dependency, or domain-specific CV logic.

- [ ] **Step 8: Commit Task 8**

```bash
git add README.md docs/architecture/README.md .codex-plugin/plugin.json tests/integration tests/test_scaffold.py
git commit -m "docs: finalize CHECK V1 core integration"
```

- [ ] **Step 9: Run final deterministic gate from a clean working tree**

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
git status --short
```

Expected: tests pass, Ruff clean, and `git status --short` prints nothing.

- [ ] **Step 10: Human acceptance checkpoint before end-to-end ChatGPT evaluation**

Review the implemented skill, report schema, validator behavior, and representative fixtures. Do not call V1 production-ready yet; deterministic correctness only establishes that the contract machinery is internally coherent. The next acceptance activity is the end-to-end ChatGPT fixture run described in `evals/release-checklist.md`.

---

## Plan Self-Review Result

### Spec coverage

- Rules 1-8: enforced through skill references, schema vocabulary, validator, and fixtures.
- Rules 9-11: implemented by expression/scoring tasks and aggregation-focused fixtures.
- Rules 12-16: represented in schema, invariant validation, skill contract, and adversarial fixtures.
- Rules 17-24: enforced through artifact scope, input roles, fixture corpus, report references, and skill boundaries.
- Rules 25-28: implemented through nested expressions, quantitative/temporal fixture coverage, proof-of-absence search scope, and documentary-vs-reality guidance.
- Ten canonical domain objects and embedded report records: schema Task 1.
- Eight-stage pipeline: runtime reference + production skill Tasks 4-5.
- Four-layer test architecture: Tasks 1-7.
- Cross-domain corpus: Task 6.
- False MET / Unnecessary UNVERIFIABLE metrics: Task 7.
- V1 no-server/no-UI/no-persistence boundary: global constraints and Task 8 integration checks.

### Type consistency

Public Python interfaces used across tasks are fixed to:

```python
schema_issues(report, path=None) -> tuple[ValidationIssue, ...]
validate_report(report, schema_path=None) -> tuple[ValidationIssue, ...]
assert_valid_report(report, schema_path=None) -> None
derive_expression_results(report) -> list[dict[str, Any]]
compute_score_summary(report, *, min_evaluable_ratio: float) -> dict[str, Any]
score_issues(report, *, min_evaluable_ratio: float) -> tuple[ValidationIssue, ...]
compute_evaluation_metrics(observations) -> EvaluationMetrics
```

No implementation task may rename these without first updating this plan and all downstream consumers.

### Scope check

The plan builds one coherent V1 subsystem: the CHECK verification primitive. Deployment/submission to the public OpenAI directory and any future MCP/UI work are separate future plans because they introduce different infrastructure and review gates.
