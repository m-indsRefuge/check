# CHECK End-to-End Evaluation

The deterministic validator proves that a CHECK report is structurally legal. These evaluations measure whether ChatGPT's semantic CHECK behavior matches the manually established fixture ground truth.

## Observation format

Record one JSON object per expected criterion or expression in a JSONL annotation file:

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

## Procedure

1. Install or open the current CHECK plugin/skill build in ChatGPT testing.
2. Run each fixture using its natural request plus the fixture requirement source and artifact.
3. Save the canonical CHECK report under `evals/results/<run-id>/<case-id>.json`.
4. Validate the report with `assert_valid_report()`. The report itself records `score_summary.threshold_used`, so score validation has no hidden threshold.
5. Map observed criteria/expression results to fixture expectation IDs manually, using source excerpts and provenance rather than generated IDs.
6. Record observations as JSONL under `evals/annotations/<run-id>.jsonl`.
7. Pass those observations to `compute_evaluation_metrics()`.
8. Manually inspect every false `MET`, requirement-logic corruption, unsupported assumption, and report-contract violation before release.

## Primary risk metrics

- **False MET Rate** = observed `MET` where expected != `MET` / all observed `MET`.
- **Unnecessary UNVERIFIABLE Rate** = observed `UNVERIFIABLE` where expected != `UNVERIFIABLE` / all observed `UNVERIFIABLE`.

A zero denominator is reported as `null`/`None`, not `0.0`, because no empirical rate was observed.
