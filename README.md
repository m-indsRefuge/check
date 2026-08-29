# CHECK

CHECK is a ChatGPT plugin for checking an artifact against explicit
requirements and identifying what is met, partially met, missing,
contradicted, or cannot be verified.

## Status

Pre-design scaffold.

The CHECK verification contract is the next design milestone.

## Core idea

Given:

1. a source of requirements; and
2. an artifact to inspect,

CHECK produces an evidence-grounded assessment of how completely the
artifact satisfies those requirements.

Potential examples include:

- CV vs. job description
- essay vs. assignment rubric
- proposal vs. submission requirements
- implementation vs. acceptance criteria
- report vs. requested deliverables
- article vs. editorial brief

## Design principles

- Evidence before verdict
- Explicit uncertainty
- No invented compliance
- Narrow core capability
- Testable against known ground truth
- No persistence unless later proven necessary
- UI only after V1 core behavior is production-ready

## Repository layout

check/
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   `-- check/
|       `-- SKILL.md
|-- tests/
|   |-- fixtures/
|   |   |-- requirements/
|   |   `-- artifacts/
|   `-- test_scaffold.py
|-- docs/
|   `-- architecture/
|-- pyproject.toml
|-- LICENSE
`-- README.md

## License

MIT
