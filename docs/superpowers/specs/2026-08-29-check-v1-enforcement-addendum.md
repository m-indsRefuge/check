# CHECK V1 Machine-Enforcement Addendum

Date: 2026-08-29
Applies to: `2026-08-29-check-v1-design.md`
Contract version: `1.0`

## Status

This addendum records representation fields required to enforce rules already approved in the CHECK V1 design. It **does not change CHECK V1 semantic meaning**, verdict definitions, scoring weights, source authority, evidence standards, or user-facing product behavior.

The approved design baseline remains authoritative for semantics. This addendum is authoritative only for these implementation-level representations.

## 1. `Criterion.artifact_scope`

Rule 21 requires evidence to respect which artifact or artifact set a criterion applies to. Each criterion therefore records:

- `mode`: `ALL_ARTIFACTS` or `SPECIFIC_ARTIFACTS`;
- `document_ids[]`: empty for `ALL_ARTIFACTS`; one or more designated artifact IDs for `SPECIFIC_ARTIFACTS`.

Cross-field validation rejects evidence or search scopes that use documents outside a specific artifact scope.

## 2. `CriterionAssessment.search_scope`

Rules 3, 22, and 27 require CHECK to distinguish missing evidence from unread or incompletely searched evidence. Each assessment therefore records:

- `document_ids[]` searched;
- `locations[]` searched where meaningful;
- `complete`: whether the relevant scope was completely inspected;
- `notes[]`: limitations or search-scope context.

`MISSING` requires `complete=true`. An `ABSENCE` criterion may be `MET` only when the relevant search scope is complete.

## 3. `RequirementExpression.members`

Rule 25 requires nested logical structure such as `(A OR B) AND C`. Expression members are typed references:

- `CRITERION` -> an atomic criterion ID;
- `EXPRESSION` -> another requirement-expression ID.

The resulting expression graph must be acyclic. Cross-field validation rejects cycles.

## 4. `ScoreSummary.threshold_used`

Rule 9 requires scores to be reproducible and to be withheld when evaluability is too weak. Each report therefore records the exact `threshold_used` for its evaluability decision, together with per-group evaluability and suppression reasons.

The threshold value itself is not fixed by this addendum. It remains a release configuration decision chosen from empirical end-to-end evaluation evidence, as required by the approved design.

## Governance

Any future change that alters verdict meaning, evidence sufficiency, requirement logic, coverage weighting, or source authority is not an implementation clarification and requires an explicit semantic-contract version decision.
