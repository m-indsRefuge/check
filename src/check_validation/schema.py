import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .models import ValidationIssue

_DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "check-report.schema.json"


def load_report_schema(path: Path | None = None) -> dict[str, Any]:
    schema_path = path or _DEFAULT_SCHEMA_PATH
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _format_path(parts: list[object]) -> str:
    if not parts:
        return "/"
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def schema_issues(
    report: Mapping[str, Any], path: Path | None = None
) -> tuple[ValidationIssue, ...]:
    validator = Draft202012Validator(load_report_schema(path))
    errors = sorted(validator.iter_errors(report), key=lambda error: list(error.absolute_path))
    return tuple(
        ValidationIssue(
            code="SCHEMA",
            path=_format_path(list(error.absolute_path)),
            message=error.message,
        )
        for error in errors
    )
