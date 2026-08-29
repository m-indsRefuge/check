# CHECK V1 Design Specification

Date: 2026-08-29
Status: Approved design baseline
Repository: `m-indsRefuge/check`
Contract version: `1.0`

## 1. Purpose

CHECK is a ChatGPT plugin that compares one or more designated artifacts against one or more explicit requirement sources and returns an evidence-grounded verification report.

The core product promise is:

> CHECK evaluates the supplied artifact against the supplied standard without moving the goalposts, inventing evidence, hiding uncertainty, or claiming more than the supplied material establishes.

Representative use cases include:

- CV against job description
- essay against rubric
- proposal against submission brief
- implementation report against acceptance criteria
- report against requested deliverables
- application against eligibility requirements
- policy or document against explicit compliance criteria

CHECK V1 is deliberately a skills-first plugin. It does not require an MCP server, custom UI, persistence layer, database, user accounts, or external model calls.

## 2. V1 Product Boundary

CHECK V1 consists of:

1. a ChatGPT skill that performs the verification workflow;
2. an authoritative semantic contract;
3. a canonical machine-readable report schema;
4. deterministic offline validation and scoring utilities;
5. a fixture and evaluation corpus with known ground truth.

The Python validator is engineering assurance infrastructure only. CHECK must function in ChatGPT without requiring that validator at runtime.

Explicitly out of scope for V1:

- MCP server
- API service
- database
- authentication
- persistent document storage
- React UI or custom widget
- embeddings or vector database
- external LLM calls
- proprietary model
- domain-specific CV logic
- user-configurable rule engine
- document-content telemetry

A future MCP runtime or UI may consume the same `CheckReport` contract without redefining CHECK semantics.

## 3. CHECK V1 Verification Contract

### Rule 1 — Source Authority

Only requirements grounded in designated requirement sources may affect compliance verdicts or scores. Non-required improvement suggestions may appear only as clearly separated advisories and must never affect compliance.

Principle: **CHECK never moves the goalposts.**

### Rule 2 — Verdict Taxonomy

CHECK uses exactly five criterion verdicts:

- `MET` — sufficient evidence satisfies the criterion.
- `PARTIAL` — meaningful relevant evidence exists, but the criterion is not fully satisfied.
- `MISSING` — the artifact was expected to demonstrate the criterion, the relevant scope was reliably inspected, and no sufficient evidence was found.
- `CONTRADICTED` — artifact evidence conflicts with the criterion.
- `UNVERIFIABLE` — compliance cannot reasonably be established from the supplied material.

### Rule 3 — Evidence Before Verdict

Every verdict must have a traceable basis. `MET`, `PARTIAL`, and `CONTRADICTED` require evidence. `UNVERIFIABLE` requires an explicit limiting condition. `MISSING` requires a documented successful search scope.

Principle: **No verdict without a traceable reason.**

### Rule 4 — Requirement Atomicity

Compound requirements are decomposed into independently verifiable atomic criteria when their components can receive different outcomes. Decomposition must preserve original meaning, thresholds, qualifiers, modality, optionality, and parent provenance.

CHECK may split a requirement but may never make it stricter.

### Rule 5 — Requirement Strength

Every atomic criterion preserves source-grounded requirement strength:

- `REQUIRED`
- `PREFERRED`
- `CONDITIONAL`
- `UNSPECIFIED`

A conditional criterion must also record `effective_strength_if_applies` as `REQUIRED`, `PREFERRED`, or `UNSPECIFIED` when the source establishes that strength. This clarification preserves the approved strength taxonomy while allowing conditional criteria to score correctly once they apply.

### Rule 6 — Conditional Applicability

Conditional criteria use one applicability state:

- `APPLIES`
- `DOES_NOT_APPLY`
- `APPLICABILITY_UNKNOWN`

Non-conditional criteria use `NOT_CONDITIONAL` internally.

`DOES_NOT_APPLY` criteria do not count toward scoring. `APPLICABILITY_UNKNOWN` must not be treated as failure. Applicability decisions must be evidence-grounded.

Principle: **A requirement cannot fail until CHECK has established that it applies.**

### Rule 7 — Preserve Source Ambiguity

CHECK preserves ambiguity instead of inventing definitions, thresholds, or stronger interpretations. Criteria are marked `CLEAR` or `AMBIGUOUS`. Any verdict on an ambiguous criterion must state the unresolved ambiguity and respect its effect on evaluability.

### Rule 8 — Source Conflict Handling

Conflicting source instructions are surfaced as `SOURCE_CONFLICT`. CHECK must preserve each conflicting statement and may resolve the conflict only when source precedence is established. Unresolved source conflicts are excluded from ordinary failure scoring.

### Rule 9 — Scoring

CHECK reports separate `Required Coverage` and `Preferred Coverage` when evaluability is sufficient.

Criterion-level scoring values are:

- `MET` = `1.0`
- `PARTIAL` = `0.5`
- `MISSING` = `0.0`
- `CONTRADICTED` = `0.0`
- `UNVERIFIABLE` = excluded

Also excluded are `DOES_NOT_APPLY`, `APPLICABILITY_UNKNOWN`, unresolved `SOURCE_CONFLICT`, and `UNSPECIFIED` criteria.

For compound requirements, scoring is performed on the derived top-level requirement-expression result rather than counting atomic alternatives independently. This prevents `A OR B` from being scored as two obligations.

Coverage measures only coverage of supplied requirements by supplied evidence. It must never be represented as suitability, quality, probability of success, or outcome probability.

Coverage percentages are withheld when evaluability is too weak to make the number meaningful. The exact release threshold is intentionally determined from evaluation evidence rather than chosen speculatively.

Principle: **The matrix is the truth; the score is only a summary.**

### Rule 10 — Evidence Specificity

Evidence uses one strength:

- `DIRECT`
- `INFERRED`
- `RELATED`

`RELATED` evidence cannot by itself support `MET`. `INFERRED` evidence may support `MET` only when the inference is straightforward, traceable, and grounded entirely in explicit artifact facts.

Principle: **Plausibility is not proof.**

### Rule 11 — Multiple Evidence Aggregation

CHECK may aggregate multiple evidence items when the requirement is cumulative and the evidence is legitimately combinable. Aggregation must expose all inputs, method, overlap treatment, uncertainty, and any constraint on combination.

Aggregation diagnostics are:

- `AGGREGATION_OK`
- `OVERLAP_DETECTED`
- `AGGREGATION_AMBIGUOUS`
- `AGGREGATION_CONFLICT`

Overlapping periods must not be double-counted. Impossible or contradictory source facts are surfaced separately as artifact-integrity findings.

### Rule 12 — Artifact Integrity

CHECK separately identifies internal artifact inconsistencies using:

- `INFO`
- `WARNING`
- `ERROR`

Integrity findings are separate from compliance verdicts and affect a verdict only when questionable evidence is required for that verdict. CHECK never silently repairs conflicting artifact facts.

Principle: **Compliance asks whether the artifact satisfies the source. Integrity asks whether the artifact agrees with itself.**

### Rule 13 — Source Precedence

When multiple requirement sources are supplied, precedence is established in this order:

1. explicit precedence stated by source documents;
2. explicit user instruction;
3. clearly established version or amendment relationship;
4. otherwise, no assumed precedence.

Recency or file metadata alone never establishes authority.

### Rule 14 — Requirement Provenance

Every atomic criterion must retain:

- stable criterion ID;
- normalized interpretation;
- original wording;
- source document;
- source location when reliably available;
- parent requirement when decomposed;
- any precedence decision affecting authority.

Principle: **Every requirement must be traceable back to the words that created it.**

### Rule 15 — Artifact Evidence Provenance

Every evidence item must retain:

- stable evidence ID;
- criterion relationship;
- exact source evidence or fact;
- artifact document;
- artifact location when reliably available;
- evidence strength;
- any derivation or aggregation applied.

Principle: **Every verdict must be traceable both to the requirement that demanded it and the artifact evidence that justified it.**

### Rule 16 — No Silent Assumptions

CHECK must identify any unstated fact needed to reach a verdict. Material assumptions cannot masquerade as evidence. A missing essential fact normally causes `UNVERIFIABLE`; a missing non-essential fact may justify `PARTIAL` where meaningful evidence still exists.

### Rule 17 — Artifact Boundary

Compliance verdicts are based on the designated artifact set. User statements outside that set are `SUPPLEMENTAL_CONTEXT`, not artifact evidence. Supplemental context may generate advisories but must not silently upgrade the artifact verdict.

Principle: **CHECK evaluates the artifact that was submitted, not the person behind it.**

### Rule 18 — Input Role Declaration

Every input has one role:

- `REQUIREMENT_SOURCE`
- `ARTIFACT`
- `SUPPLEMENTAL_CONTEXT`

User-declared roles take precedence. CHECK may infer roles only when context is sufficiently clear. Scoring must not begin if material role uncertainty remains.

### Rule 19 — Scope Control

Candidate source statements are classified as:

- `REQUIREMENT`
- `CONTEXT`
- `UNCERTAIN_SCOPE`

Context does not enter the compliance matrix. Uncertain scope is surfaced rather than silently converted into a requirement.

Principle: **CHECK extracts standards, not sentences.**

### Rule 20 — Requirement Duplication and Equivalence

Equivalent or materially overlapping requirements are represented once as a canonical obligation while preserving all relevant source provenance. Repetition must not distort scoring.

Principle: **Repeated wording does not create repeated obligations.**

### Rule 21 — Multi-Artifact Evaluation

CHECK may evaluate an artifact set. Evidence must preserve which artifact supplied it. Evidence from one artifact may satisfy a criterion applied to another artifact only when the requirement permits that cross-artifact evidence.

### Rule 22 — Extraction Failure and Input Quality

CHECK must never pretend to have inspected material that could not be reliably read. Corrupted, inaccessible, truncated, unsupported, illegible, or partially extracted material must generate explicit limitations and affected verdicts or scores must be withheld.

Principle: **Unread evidence is not missing evidence.**

### Rule 23 — Explicit Uncertainty

CHECK represents uncertainty semantically and explains its cause. V1 does not emit arbitrary numerical model-confidence percentages.

Relevant uncertainty sources include ambiguity, weak evidence, applicability uncertainty, extraction failure, conflicting evidence, and incomplete source material.

### Rule 24 — Report Completeness and Repair Guidance

A completed report must contain a verification summary, requirement matrix, exceptions and limitations, and clearly separated advisories. For `PARTIAL`, `MISSING`, or `CONTRADICTED` criteria, CHECK may state what evidence or artifact change would resolve the gap but must not fabricate qualifications, claims, facts, or compliance.

Principle: **A CHECK result should identify both the gap and what would resolve it.**

### Rule 25 — Requirement Logic and Alternatives

Atomic decomposition must preserve logical relationships including `AND`, `OR`, either/or alternatives, `AT_LEAST_N_OF`, conditions, and prohibitions.

V1 canonical expression operators are:

- `SINGLE`
- `ALL_OF`
- `ANY_OF`
- `AT_LEAST_N_OF`

Logical expressions receive derived expression results after criterion assessment. These expression results are used for top-level obligation reporting and compound-requirement scoring.

Principle: **CHECK may decompose requirements without destroying their logic.**

### Rule 26 — Quantitative and Temporal Semantics

CHECK may normalize dates, durations, ranges, counts, percentages, and units for comparison, but normalization must preserve source meaning. Inclusive and exclusive thresholds, approximation, precision limits, and temporal overlap must remain explicit.

Principle: **Normalization may change representation, never meaning.**

### Rule 27 — Prohibitions and Proof of Absence

Negative requirements require evidence that the relevant scope was completely inspected. CHECK may claim absence only over material it reliably inspected. If relevant content extraction is incomplete, absence-dependent criteria become `UNVERIFIABLE` rather than `MET`.

Principle: **Absence can only be proven over material CHECK has actually inspected.**

### Rule 28 — Documentary Compliance vs Real-World Truth

CHECK evaluates what supplied evidence establishes. A claim appearing in an artifact may establish documentary coverage without independently proving that the claim is true in the external world. Independent verification is recognized only when suitable verification evidence is explicitly supplied.

Principle: **CHECK verifies what the supplied evidence establishes; it does not certify external reality.**

## 4. Canonical Domain Model

CHECK V1 uses ten canonical top-level domain objects. Small embedded records such as advisories, source-conflict records, and expression-result records are intentionally not promoted into additional top-level domain entities.

### 4.1 `CheckRequest`

Purpose: defines one verification operation.

Fields:

- `request_id`
- `inputs[]`
- `requested_scope`
- `user_instructions[]`

Invariants:

- at least one `REQUIREMENT_SOURCE`;
- at least one `ARTIFACT`;
- optional supplemental context;
- material role uncertainty prevents scoring.

### 4.2 `InputDocument`

Purpose: represents each supplied document or text input.

Fields:

- `document_id`
- `role`
- `display_name`
- `media_type`
- `content_status`
- `extraction_quality`
- `limitations[]`

`content_status`:

- `AVAILABLE`
- `PARTIAL`
- `UNREADABLE`
- `UNAVAILABLE`

`extraction_quality`:

- `COMPLETE`
- `DEGRADED`
- `UNKNOWN`

V1 uses qualitative extraction states rather than invented numeric confidence.

### 4.3 `SourceSpan`

Purpose: immutable provenance primitive shared by requirements and artifact evidence.

Fields:

- `span_id`
- `document_id`
- `location`
- `exact_text`
- optional `normalized_fact`

`exact_text` must preserve supplied wording. Normalization is stored separately.

### 4.4 `Criterion`

Purpose: one atomic requirement.

Fields:

- `criterion_id`
- optional `parent_id`
- `normalized_requirement`
- `original_spans[]`
- `strength`
- optional `effective_strength_if_applies`
- `interpretation_state`
- `applicability`
- `requirement_kind`
- optional `threshold`
- optional `prohibition`
- optional `source_precedence`

`strength`:

- `REQUIRED`
- `PREFERRED`
- `CONDITIONAL`
- `UNSPECIFIED`

`effective_strength_if_applies` is required for a conditional criterion when the source establishes whether the obligation is required or preferred once applicable.

`interpretation_state`:

- `CLEAR`
- `AMBIGUOUS`

`applicability`:

- `APPLIES`
- `DOES_NOT_APPLY`
- `APPLICABILITY_UNKNOWN`
- `NOT_CONDITIONAL`

`requirement_kind`:

- `PRESENCE`
- `ABSENCE`
- `QUANTITATIVE`
- `QUALITATIVE`
- `TEMPORAL`
- `OTHER`

### 4.5 `RequirementExpression`

Purpose: preserves logical relationships between criteria without destroying atomicity.

Fields:

- `expression_id`
- `operator`
- `members[]`
- optional `minimum_satisfied`
- optional `condition`
- `provenance[]`

Operators:

- `SINGLE`
- `ALL_OF`
- `ANY_OF`
- `AT_LEAST_N_OF`

Expressions do not implement an arbitrary programming language.

### 4.6 `EvidenceItem`

Purpose: represents evidence found in designated artifacts.

Fields:

- `evidence_id`
- `criterion_ids[]`
- `source_spans[]`
- `strength`
- optional `derived_value`
- optional `derivation`
- `reliability_notes[]`

Evidence strength:

- `DIRECT`
- `INFERRED`
- `RELATED`

Derived values must expose their source facts and derivation method.

### 4.7 `CriterionAssessment`

Purpose: maps one atomic criterion to its evidence-grounded verdict.

Fields:

- `assessment_id`
- `criterion_id`
- `verdict`
- `evidence_ids[]`
- `reasoning`
- `uncertainty_notes[]`
- optional `aggregation_status`
- `integrity_impacts[]`
- optional `repair_guidance`

Decision order:

1. If the criterion cannot be evaluated reliably: `UNVERIFIABLE`.
2. Else if explicit artifact evidence conflicts with it: `CONTRADICTED`.
3. Else if it is fully satisfied: `MET`.
4. Else if meaningful but incomplete evidence exists: `PARTIAL`.
5. Else: `MISSING`.

Evidence invariants:

- `MET` requires evidence;
- `PARTIAL` requires evidence;
- `CONTRADICTED` requires conflicting evidence;
- `UNVERIFIABLE` requires a limiting condition;
- `MISSING` requires a successfully inspected search scope.

`repair_guidance` is allowed for `PARTIAL`, `MISSING`, and `CONTRADICTED` only and must never fabricate user facts.

Assessments are immutable within a report version. A changed artifact produces a new report.

### 4.8 `IntegrityFinding`

Purpose: records internal artifact consistency problems separately from compliance.

Fields:

- `finding_id`
- `severity`
- `category`
- `affected_document_ids[]`
- `source_spans[]`
- `description`
- `affected_criterion_ids[]`
- `impact`

Severity:

- `INFO`
- `WARNING`
- `ERROR`

Initial categories:

- `CONTRADICTORY_FACTS`
- `IMPOSSIBLE_VALUE`
- `DUPLICATE_CONFLICT`
- `TEMPORAL_CONFLICT`
- `AGGREGATION_CONFLICT`
- `OTHER`

Impact:

- `NO_VERDICT_IMPACT`
- `LIMITS_VERIFICATION`
- `INVALIDATES_EVIDENCE`

### 4.9 `ScoreSummary`

Purpose: derived summary only. It must never make new semantic decisions.

Fields:

- optional `required_coverage`
- optional `preferred_coverage`
- `required_counts`
- `preferred_counts`
- `unspecified_counts`
- `excluded_counts`
- `evaluability`
- optional `suppression_reason`

Evaluability:

- `SUFFICIENT`
- `INSUFFICIENT`

For simple single criteria, criterion assessments are the scoring units. For compound logical obligations, the scoring unit is the top-level expression result so that alternatives are not double-counted.

### 4.10 `CheckReport`

Purpose: complete authoritative result.

Fields:

- `report_id`
- `contract_version`
- `request`
- `inputs[]`
- `criteria[]`
- `requirement_expressions[]`
- `expression_results[]`
- `evidence[]`
- `assessments[]`
- `integrity_findings[]`
- `source_conflicts[]`
- `score_summary`
- `limitations[]`
- `advisories[]`
- `generated_at`

The report must be self-contained enough to reconstruct what was checked, which criteria were extracted, which logical obligations they formed, which evidence was used, every verdict, every exclusion, and every limitation.

`source_conflicts[]`, `expression_results[]`, and `advisories[]` are embedded report records rather than additional canonical domain entities.

## 5. Embedded Report Records

### 5.1 Expression Result

Compound logical obligations require a derived top-level result so atomic alternatives do not distort user-facing compliance or scoring.

An expression result records:

- `expression_id`
- `verdict`
- `member_assessment_ids[]`
- `reasoning`
- `score_strength`
- `excluded_reason` when applicable

General behavior:

- `SINGLE`: inherits the member criterion assessment.
- `ALL_OF`: `MET` only when all applicable required members are fully satisfied; incomplete but meaningful member coverage may produce `PARTIAL`.
- `ANY_OF`: `MET` when at least one permitted alternative fully satisfies the obligation; absent alternatives do not count as separate failures once the expression is satisfied.
- `AT_LEAST_N_OF`: `MET` when the specified number of alternatives are satisfied.
- unresolved uncertainty that prevents reliable logical evaluation produces `UNVERIFIABLE` at the expression level.
- an expression is `CONTRADICTED` only when explicit conflicting evidence defeats all viable satisfaction paths; one contradicted alternative does not automatically contradict an otherwise satisfiable `ANY_OF` expression.

Expression results, not atomic alternative counts, are authoritative for compound-obligation scoring.

### 5.2 Source Conflict Record

Records:

- conflicting source spans;
- affected criteria or expressions;
- precedence information considered;
- whether the conflict was resolved;
- resolution basis when resolved.

### 5.3 Advisory Record

Records:

- `advisory_id`
- `observation`
- `supporting_spans[]`
- `related_criterion_ids[]`

Advisories receive no compliance verdict and no score weight.

## 6. Processing Pipeline

CHECK V1 uses an eight-stage fail-closed pipeline.

### Stage 1 — Input Classification

Determine input roles and construct `CheckRequest` and `InputDocument[]`.

Stop before verification if CHECK cannot reliably identify the requirement source and artifact roles.

### Stage 2 — Content Extraction and Quality Assessment

Determine what material was actually available and reliably inspectable. Record extraction completeness and limitations before interpreting absence.

Outputs include document quality states and traceable `SourceSpan` records.

### Stage 3 — Requirement Modeling

Process only designated requirement sources to perform:

- requirement versus context separation;
- atomic decomposition;
- requirement strength classification;
- conditional modeling;
- ambiguity detection;
- duplicate and equivalent requirement consolidation;
- source precedence;
- source conflict detection;
- quantitative and temporal normalization;
- logical-expression construction.

Requirement modeling must occur independently of artifact contents so the observed artifact cannot alter what CHECK decides the source required.

### Stage 4 — Evidence Discovery

Only after the requirement model is fixed, inspect the designated artifact set for direct, inferred, related, conflicting, cumulative, and overlapping evidence.

Evidence discovery records candidate evidence but does not assign final criterion verdicts.

Principle: **Finding evidence and judging evidence are separate operations.**

### Stage 5 — Criterion and Expression Assessment

Assess every applicable atomic criterion using the deterministic verdict decision boundary, then derive logical expression results from member assessments.

Conditional criteria that do not apply never enter ordinary failure scoring.

### Stage 6 — Artifact Integrity Pass

Detect internal inconsistencies after evidence discovery, when CHECK has enough structure to identify contradictions, impossible values, duplicate conflicts, temporal problems, and aggregation conflicts.

If an integrity finding invalidates or limits evidence used by an assessment, affected assessments and expression results are recalculated before scoring.

### Stage 7 — Scoring and Advisory Pass

Once verdicts are stable:

- calculate required and preferred coverage when permitted;
- calculate verdict and exclusion counts;
- evaluate score sufficiency;
- generate clearly separated non-scoring advisories.

Advisories occur after compliance determination so they cannot contaminate requirements.

### Stage 8 — Report Validation and Emission

Validate the canonical report against structural and cross-field invariants before returning the user-facing result.

Examples of invalid reports include:

- `MET` with no evidence;
- `CONTRADICTED` with no conflicting evidence;
- unsupported `MISSING` after incomplete relevant extraction;
- criterion with no requirement provenance;
- evidence with no artifact provenance;
- advisory contributing to score;
- `DOES_NOT_APPLY` included in denominator;
- compound alternatives independently counted when their expression is the actual obligation.

CHECK should fail closed: provide what can be established, but convert affected claims to explicit uncertainty rather than confidently degrading.

## 7. Human-Facing Report

The canonical `CheckReport` is machine-readable and audit-oriented. The default user-facing rendering is concise and contains five sections:

1. Summary
2. Priority Gaps
3. Verification Matrix
4. Integrity and Limitations
5. Advisory Observations

### Summary

Shows required and preferred coverage when valid, plus verdict counts and any score suppression.

### Priority Gaps

Prioritize:

1. required `MISSING` criteria;
2. required `CONTRADICTED` criteria;
3. required `PARTIAL` criteria;
4. `UNVERIFIABLE` criteria and uncertainty;
5. preferred gaps.

### Verification Matrix

Shows human-readable requirement, strength, verdict, evidence, and concise justification. Compound logical obligations must be rendered in a way that makes alternative satisfaction clear.

### Integrity and Limitations

Shows artifact integrity findings, source conflicts, extraction limitations, ambiguity, applicability uncertainty, and other material constraints.

### Advisory Observations

Contains useful non-requirement observations that never affect compliance.

The user-facing result is derived from the canonical report and may not contradict it.

## 8. Interaction Policy

CHECK should not interrogate the user unnecessarily.

Ask a clarifying question only when proceeding would materially corrupt the verification, for example:

- requirement-source versus artifact roles cannot be determined;
- source precedence is necessary to resolve an otherwise blocking conflict;
- the user's requested evaluation depends on a conditional fact that cannot be established and cannot safely remain unresolved.

Do not interrupt merely because:

- a requirement is missing;
- a preferred item is absent;
- ambiguity can be reported explicitly;
- a requirement can simply be marked `UNVERIFIABLE`.

CHECK diagnoses first. Artifact repair or rewriting is a separate user-requested action.

## 9. Repository Architecture

Target V1 structure:

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
│       ├── validate.py
│       └── scoring.py
├── tests/
│   ├── contract/
│   ├── fixtures/
│   │   ├── cv-job/
│   │   ├── essay-rubric/
│   │   ├── proposal-brief/
│   │   ├── software-acceptance/
│   │   ├── report-deliverables/
│   │   ├── eligibility/
│   │   └── policy/
│   ├── adversarial/
│   └── test_scaffold.py
├── evals/
│   ├── cases/
│   └── README.md
├── docs/
│   └── architecture/
├── pyproject.toml
└── README.md
```

### Skill

`skills/check/SKILL.md` is the actual V1 runtime behavior and implements the eight-stage workflow. Deeper reference documents prevent the skill file from becoming an unmaintainable monolith.

### Canonical Schema

`schemas/check-report.schema.json` defines the stable result boundary shared by fixtures, validators, future MCP tools, and future UI.

### Offline Validator

`src/check_validation/` performs deterministic functions only, including:

- schema validation;
- cross-field invariant enforcement;
- coverage calculation;
- verdict/evidence legality checks;
- fixture expectation validation.

It must not attempt to reproduce semantic model reasoning. For example, it may reject `MET` with no evidence, but it must not decide whether a job title semantically proves escalation-handling experience.

## 10. Test Architecture

CHECK uses four testing layers.

### Layer 1 — Contract Tests

Deterministic tests for schema and invariant enforcement.

Representative failures:

- `MET` without evidence;
- `CONTRADICTED` without conflicting evidence;
- `MISSING` after unreadable relevant artifact scope;
- criterion without requirement provenance;
- advisory contributing to score;
- `DOES_NOT_APPLY` included in denominator;
- `RELATED` evidence alone supporting `MET`;
- independently scoring alternatives from a satisfied `ANY_OF` expression.

### Layer 2 — Semantic Fixture Tests

Each fixture includes requirement material, artifact material, expected canonical outcomes, and explanatory fixture documentation.

Fixtures establish known ground truth for requirement extraction, evidence mapping, verdicts, expression behavior, provenance, and score calculation.

### Layer 3 — Adversarial Fixtures

Adversarial cases target specific contract failure modes including:

- goalpost expansion;
- plausible-but-unproven evidence;
- false proof of absence;
- overlapping duration double-counting;
- ambiguous threshold invention;
- documentary claims mistaken for externally verified truth;
- logical `OR` corruption;
- duplicate-requirement score inflation;
- incomplete extraction misclassified as missing.

### Layer 4 — End-to-End Plugin Evaluations

Run representative ChatGPT conversations against fixtures and compare generated results with expected outcomes.

Tracked semantic metrics include:

- requirement extraction accuracy;
- over-extraction;
- requirement omission;
- verdict accuracy;
- evidence attribution accuracy;
- source-grounding failures;
- logic preservation;
- unsupported assumptions;
- report-contract violations;
- `False MET Rate`;
- `Unnecessary UNVERIFIABLE Rate`.

The two primary semantic-risk metrics are:

1. **False MET Rate** — CHECK incorrectly reports compliance.
2. **Unnecessary UNVERIFIABLE Rate** — CHECK is more conservative than the evidence requires.

The first protects trustworthiness; the second protects usefulness.

## 11. Initial Fixture Families

The release corpus should span at least:

- CV ↔ job description
- essay ↔ rubric
- proposal ↔ submission brief
- implementation report ↔ acceptance criteria
- report ↔ requested deliverables
- application ↔ eligibility requirements
- policy/document ↔ explicit compliance criteria

The purpose of cross-domain coverage is to demonstrate that CHECK implements a general verification primitive rather than hidden domain-specific logic.

## 12. V1 Release Gate

Before CHECK V1 is considered production-ready:

1. all deterministic contract tests pass;
2. there are zero known schema or invariant violations;
3. there are zero known unsupported `MET` verdicts in the release corpus;
4. no known requirement-logic corruption remains in the release corpus;
5. every verdict is traceable to requirement source and artifact evidence or limiting condition;
6. extraction limitations are correctly surfaced;
7. all coverage scores are reproducible from authoritative assessments and expression results;
8. a representative cross-domain sample receives manual review.

Numeric semantic accuracy thresholds are set only after the initial corpus exists and baseline evaluation data has been collected.

## 13. Versioning

Plugin version and semantic contract version are separate.

Example:

- plugin version: `0.4.2`
- contract version: `1.0`

Bug fixes or packaging changes need not change the contract version. Any material semantic change to verdict meaning, scoring semantics, requirement logic, or evidence standards requires an explicit contract-version decision.

## 14. Reasoning Transparency Boundary

CHECK reports concise, auditable justifications and provenance. It does not store or expose private model chain-of-thought.

A valid justification explains the observable basis for the outcome, for example:

> The artifact lists Zendesk under Technical Skills, directly satisfying the preferred Zendesk-experience criterion.

This is sufficient for auditability without preserving hidden reasoning traces.

## 15. Architectural Principles

The V1 architecture is governed by these principles:

- evidence before verdict;
- source authority before advisory judgment;
- explicit uncertainty before invented certainty;
- provenance on both sides of every verdict;
- logical preservation during atomic decomposition;
- fail-closed behavior under unreliable input;
- deterministic structural enforcement where possible;
- semantic evaluation through fixtures and end-to-end evals;
- no runtime infrastructure until evidence proves it is necessary;
- UI only after the V1 core is production-ready and deployed.

The V1 architectural summary is:

> **CHECK is a skill with a contract, not a service pretending to be a skill.**

## 16. Approved Processing Summary

```text
Requirement source(s) + artifact(s) + optional supplemental context
                              │
                              ▼
                    Input classification
                              │
                              ▼
                 Extraction quality assessment
                              │
                              ▼
                    Requirement modeling
                              │
                              ▼
                     Evidence discovery
                              │
                              ▼
              Criterion + expression assessment
                              │
                              ▼
                    Artifact integrity pass
                              │
                     affected? ── yes ──┐
                              │          │
                              └──────────┘ re-assess
                              │
                              ▼
                    Scoring + advisories
                              │
                              ▼
                    Contract validation
                              │
                              ▼
                        CHECK REPORT
```

This document is the approved CHECK V1 architectural and semantic design baseline. Implementation must preserve these boundaries unless later evidence demonstrates that the contract itself requires amendment.