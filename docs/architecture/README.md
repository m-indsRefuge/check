# CHECK Architecture

CHECK V1 is intentionally skills-first.

```text
ChatGPT
  -> CHECK skill
  -> canonical CheckReport

Offline engineering assurance only:
  -> JSON Schema validation
  -> cross-field invariant validation
  -> logical-expression derivation
  -> coverage scoring
  -> fixture/evaluation metrics
```

The skill and its reference documents define the runtime workflow. The canonical `CheckReport` schema defines the machine-readable boundary that future runtimes or UI layers may consume.

The Python code under `src/check_validation/` is not called by the skill in V1. It exists to prove deterministic properties of reports and evaluation data during development and release verification.

## Explicit V1 exclusions

V1 contains no MCP server, API service, database, authentication system, persistent document storage, React/custom UI, vector store, network client, or external model integration.

If later evidence shows that runtime enforcement or a visual verification matrix materially improves CHECK, those capabilities can be added behind the existing report contract without changing the meaning of CHECK.
