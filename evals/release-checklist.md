# CHECK V1 End-to-End Release Checklist

CHECK is not production-ready merely because deterministic tests pass.

Before release:

- Run the representative cross-domain and adversarial corpus in ChatGPT.
- Validate every emitted canonical report with `assert_valid_report()`.
- Record manual expectation mappings and compute semantic metrics.
- Investigate every false `MET` before release; zero known unsupported `MET` verdicts is a release gate.
- Investigate every requirement-logic corruption and report-contract violation.
- Review the Unnecessary UNVERIFIABLE Rate so safety is not achieved by making CHECK uselessly conservative.
- Manually review representative provenance, ambiguity, extraction-limitation, conditional-applicability, source-conflict, and documentary-vs-reality cases.

## Evaluability threshold selection

`min_evaluable_ratio` remains a release configuration decision until baseline end-to-end runs exist. Do not hard-code a speculative default into the CHECK skill or deterministic validator.

For the release candidate, record:

1. the chosen threshold;
2. the corpus/run IDs used to choose it;
3. coverage suppression behavior at nearby candidate thresholds; and
4. the empirical justification for the final value.
