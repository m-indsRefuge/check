# CHECK

CHECK is a skills-first ChatGPT plugin for checking a designated artifact or artifact set against explicit requirement sources.

It answers a narrow question rigorously: **what does this artifact satisfy, partially satisfy, miss, contradict, or leave unverifiable against the supplied standard?**

## V1 core status

The CHECK V1 deterministic core is implemented for engineering verification. Public-directory submission and end-to-end ChatGPT semantic evaluation are separate release activities and must complete before CHECK is called production-ready.

## Verdicts

CHECK uses exactly five criterion verdicts:

- `MET` — sufficient artifact evidence satisfies the criterion.
- `PARTIAL` — meaningful evidence exists, but coverage is incomplete.
- `MISSING` — the relevant artifact scope was completely inspected and sufficient evidence was not found.
- `CONTRADICTED` — artifact evidence conflicts with the criterion.
- `UNVERIFIABLE` — the supplied material cannot support a reliable conclusion.

The verification matrix is authoritative. Required and preferred coverage percentages are secondary summaries and may be withheld when too little of the requirement set is evaluable.

## What CHECK does not do

CHECK does not invent requirements that are absent from the supplied standard. Advice that is not a source requirement is separated as advisory and never affects coverage.

CHECK also distinguishes documentary coverage from external truth. For example, a CV that states a certification can satisfy a documentary requirement, but CHECK does not claim the issuer independently verified that certification unless verification evidence was supplied.

## Runtime boundary

V1 has no MCP server, API service, database, authentication, persistent document storage, external LLM call, or custom UI. The runtime product is the CHECK skill and its reference contract.

Python code under `src/check_validation/` is **offline engineering-assurance tooling only**. It validates canonical reports, enforces deterministic invariants, derives logical-expression results and reproducible scores, and computes evaluation metrics. The ChatGPT skill does not call this Python tooling at runtime.

## Core flow

1. classify requirement sources, artifacts, and supplemental context;
2. establish extraction quality;
3. model requirements independently of artifact evidence;
4. discover evidence in the designated artifact scope;
5. assess atomic criteria and logical expressions;
6. inspect artifact integrity and reassess affected evidence;
7. derive coverage and separate advisories;
8. validate the report contract and render the human-facing result.

## Evaluation

The repository contains baseline fixtures across CV/job, essay/rubric, proposal/brief, software acceptance, report deliverables, eligibility, and policy use cases, plus adversarial fixtures for known verification risks.

The two primary semantic-risk metrics are:

- **False MET Rate** — how often CHECK says `MET` when ground truth says otherwise.
- **Unnecessary UNVERIFIABLE Rate** — how often CHECK refuses a conclusion that ground truth shows was supportable.

False `MET` is release-critical. Excessive `UNVERIFIABLE` is tracked so conservatism does not make the checker useless.

## Local engineering checks

```text
uv sync --dev
uv run pytest -q
uv run ruff check .
```

The JSON schemas live under `schemas/`; end-to-end evaluation procedure and release gates live under `evals/`.

## Future work

An MCP runtime or interactive CHECK matrix UI may be added only after the skills-first V1 core is production-ready and deployed. Those additions must consume the same CHECK contract rather than redefine it.

## License

MIT
