# CHECK Report Format

The canonical `CheckReport` is the authoritative audit object. The human-facing result is a concise rendering of that report and may never contradict it.

## Canonical report requirements

A complete report records: request and input roles; extraction quality; source spans; atomic criteria; logical expressions and derived expression results; evidence; criterion assessments; artifact-integrity findings; source conflicts; deterministic score summary; limitations; advisories; contract version; and generation timestamp.

Every criterion must retain requirement provenance. Every evidence item must retain artifact provenance. Every verdict must expose concise reasoning and the evidence or limiting condition that supports it. Do not output hidden chain-of-thought.

## Human-facing order

1. Summary
2. Priority Gaps
3. Verification Matrix
4. Integrity and Limitations
5. Advisory Observations

### Summary
Show Required Coverage and Preferred Coverage only when evaluability is sufficient. Show verdict counts and explain score suppression when percentages are withheld. Never describe coverage as probability, suitability, quality, or likelihood of success.

### Priority Gaps
Order actionable issues by impact: required `MISSING`, required `CONTRADICTED`, required `PARTIAL`, material `UNVERIFIABLE`/uncertainty, then preferred gaps. Explain what genuine evidence or artifact change would resolve each gap without inventing facts.

### Verification Matrix
For each top-level obligation, show requirement text, source-grounded strength, verdict, concise evidence, and concise reason. Preserve logical alternatives so `A OR B` is visibly one obligation rather than two failures. Provide detailed provenance when requested.

### Integrity and Limitations
Surface artifact integrity findings, unresolved source conflicts, extraction limitations, source ambiguity, applicability uncertainty, and any other constraint that limits conclusions.

### Advisory Observations
Keep non-requirement observations separate. State clearly that an advisory was not required by the supplied source and does not affect coverage.

## Clarification policy
Ask a question only when continuing would materially corrupt the verification: unresolved input roles, blocking source precedence, or a requested conditional evaluation that cannot safely remain unresolved. Otherwise report ambiguity or unverifiability directly.
