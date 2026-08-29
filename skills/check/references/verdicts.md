# CHECK Verdict and Expression Rules

## Criterion decision order

Apply this order after applicability, input quality, and source-conflict handling:

1. Cannot evaluate reliably -> `UNVERIFIABLE`
2. Explicit conflicting evidence -> `CONTRADICTED`
3. Fully satisfied -> `MET`
4. Meaningful incomplete evidence -> `PARTIAL`
5. Otherwise, after complete search -> `MISSING`

### `MET`
The artifact contains sufficient evidence to satisfy the criterion as written. Requires at least one `DIRECT` or sufficiently traceable `INFERRED` evidence item. `RELATED` evidence alone is insufficient.

### `PARTIAL`
Meaningful relevant evidence exists but one or more material parts remain incomplete, weak, ambiguous, or absent. Requires evidence.

### `MISSING`
The artifact was expected to demonstrate the criterion, the relevant artifact scope was reliably and completely searched, and no sufficient evidence was found. Never use `MISSING` as a synonym for uncertainty.

### `CONTRADICTED`
Artifact evidence explicitly conflicts with the criterion. Requires traceable conflicting evidence.

### `UNVERIFIABLE`
The supplied material cannot reliably establish compliance. State the limiting condition: incomplete extraction, material ambiguity, applicability uncertainty, unresolved conflict, missing essential fact, future/external verification, or invalidated evidence.

## Evidence strength

- `DIRECT`: the artifact explicitly demonstrates the relevant fact.
- `INFERRED`: a straightforward derivation from explicit artifact facts; expose source facts and derivation.
- `RELATED`: relevant context that does not establish the criterion. Never use alone for `MET`.

## Logical expressions

Atomic criteria remain individually assessed, but compound obligations receive a derived expression result and are scored once at their root expression.

- `SINGLE`: inherit the sole applicable member.
- `ALL_OF`: `MET` only when all applicable members are `MET`; contradiction in a required member yields `CONTRADICTED`; meaningful incomplete coverage yields `PARTIAL`; otherwise use `MISSING` or `UNVERIFIABLE` according to the evidence boundary.
- `ANY_OF`: any `MET` makes the expression `MET`; otherwise `PARTIAL` if an alternative has partial coverage; otherwise `UNVERIFIABLE` when an unresolved path could change the result; all contradicted alternatives yield `CONTRADICTED`; otherwise `MISSING`.
- `AT_LEAST_N_OF`: `MET` when N members are met; `PARTIAL` when met+partial can reach N; `UNVERIFIABLE` when unresolved members could change whether N is reached; otherwise `CONTRADICTED` or `MISSING` as supported.

A non-applicable conditional alternative does not become a failure. An unresolved source conflict or applicability-unknown path may make the containing expression `UNVERIFIABLE` when it can change the outcome.
