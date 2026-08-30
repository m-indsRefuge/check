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
- `references/style.md`

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
