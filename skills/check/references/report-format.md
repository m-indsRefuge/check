# CHECK Report Format

The canonical `CheckReport` is the authoritative audit object. The human-facing result is a concise rendering of that report and may never contradict it. Apply `style.md` when rendering the human-facing result.

## Canonical report requirements

A complete report records: request and input roles; extraction quality; source spans; atomic criteria; logical expressions and derived expression results; evidence; criterion assessments; artifact-integrity findings; source conflicts; deterministic score summary; limitations; advisories; contract version; and generation timestamp.

Every criterion must retain requirement provenance. Every evidence item must retain artifact provenance. Every verdict must expose concise reasoning and the evidence or limiting condition that supports it. Do not output hidden chain-of-thought.

## Human-facing order

1. Summary
2. Priority Gaps
3. Verification Matrix
4. Integrity and Limitations
5. Advisory Observations

Keep this order when the section has content. Empty sections may be reduced to a short `None` statement or omitted when omission cannot hide a meaningful result or limitation.

### Summary

Lead with the governing result in plain language. Show Required Coverage and Preferred Coverage only when relevant and evaluability is sufficient. Explain score suppression when percentages are withheld. Never describe coverage as probability, suitability, quality, or likelihood of success.

Do not routinely narrate successful input classification, instruction/data separation, or other internal pipeline steps. Mention them only when they materially affect the result.

### Priority Gaps

Order actionable issues by impact: required `MISSING`, required `CONTRADICTED`, required `PARTIAL`, material `UNVERIFIABLE`/uncertainty, then preferred gaps. Explain what genuine evidence, clarification, or artifact change would resolve each gap without inventing facts.

When there is no actionable gap, say so briefly rather than restating satisfied requirements.

### Verification Matrix

The canonical structure remains a verification matrix, but the human-facing rendering uses **stacked requirement blocks**. **Do not use Markdown tables** for requirement results.

Render each top-level obligation approximately as:

> ### R1 — Requirement text — `VERDICT`  
> **Strength:** REQUIRED  
> **Evidence:** `artifact.txt:3` — concise evidence text  
> **Reason:** Concise ordinary-language explanation of why the evidence does or does not satisfy the requirement.

Use short provenance labels such as `artifact.txt:3` and `requirements.txt:1`. **Do not show absolute local filesystem paths** in ordinary output. Detailed provenance remains available when requested.

Preserve logical alternatives as one top-level obligation. Alternative branches may appear beneath the obligation as compact detail, but a non-selected alternative must not look like an additional scored failure.

Example:

> ### Cloud-platform experience — `MET`  
> **Strength:** REQUIRED  
> **Evidence:** `artifact.txt:1` — “Cloud platforms: Azure.”  
> **Reason:** Azure satisfies one of the allowed alternatives.  
> **Alternative detail:** AWS — no evidence found, non-failing alternative; Azure — satisfied.

#### Source-conflict rendering

For unresolved source conflicts, the governing obligation remains `UNVERIFIABLE` until precedence is established. Do not render the conflicting branches as peer scored verdicts.

Use a separate **Diagnostic detail** block when conditional comparisons are useful. These branch observations are **diagnostic only** and **not scored separately**.

Example:

> ### Support-experience threshold — `UNVERIFIABLE`  
> **Reason:** The source gives two different minimums—3 years and 5 years—and does not say which one governs. The artifact shows four years, so CHECK cannot determine compliance until the governing threshold is clarified.  
> **Diagnostic detail:**  
> - Against the 3-year threshold, four years would satisfy it.  
> - Against the 5-year threshold, four years would not satisfy it.  
> These observations do not create separate compliance scores.

### Integrity and Limitations

Surface artifact integrity findings, unresolved source conflicts, extraction limitations, source ambiguity, applicability uncertainty, and any other constraint that limits conclusions.

Explain the practical consequence first. Avoid generic disclaimers that add no useful information. Documentary-vs-real-world limitations should be shown when materially relevant, not repeated mechanically on every result.

### Advisory Observations

Keep non-requirement observations separate. When advisories exist, make clear that they were not required by the supplied source and do not affect coverage. Do not manufacture an advisory merely to populate the section.

## Clarification policy

Ask a question only when continuing would materially corrupt the verification: unresolved input roles, blocking source precedence, or a requested conditional evaluation that cannot safely remain unresolved. Otherwise report ambiguity or unverifiability directly.
