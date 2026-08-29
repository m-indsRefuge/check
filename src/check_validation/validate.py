from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .models import ValidationIssue
from .schema import schema_issues


def _issue(code: str, path: str, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, path=path, message=message)


def _index_by_id(
    items: Sequence[Mapping[str, Any]], key: str
) -> tuple[dict[str, Mapping[str, Any]], list[ValidationIssue]]:
    index: dict[str, Mapping[str, Any]] = {}
    issues: list[ValidationIssue] = []
    for position, item in enumerate(items):
        value = item.get(key)
        if not isinstance(value, str):
            continue
        if value in index:
            issues.append(
                _issue(
                    "DUPLICATE_ID",
                    f"/{key}/{position}",
                    f"Duplicate {key} value {value!r}.",
                )
            )
            continue
        index[value] = item
    return index, issues


def _require_reference(
    value: str,
    index: Mapping[str, Mapping[str, Any]],
    path: str,
    label: str,
    issues: list[ValidationIssue],
) -> Mapping[str, Any] | None:
    target = index.get(value)
    if target is None:
        issues.append(
            _issue(
                "REFERENCE_NOT_FOUND",
                path,
                f"Referenced {label} {value!r} does not exist.",
            )
        )
    return target


def _detect_expression_cycles(
    expressions: Mapping[str, Mapping[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    state: dict[str, int] = {}
    stack: list[str] = []
    reported: set[tuple[str, ...]] = set()

    def visit(expression_id: str) -> None:
        current_state = state.get(expression_id, 0)
        if current_state == 2:
            return
        if current_state == 1:
            try:
                start = stack.index(expression_id)
            except ValueError:
                start = 0
            cycle = tuple(stack[start:] + [expression_id])
            if cycle not in reported:
                reported.add(cycle)
                issues.append(
                    _issue(
                        "EXPRESSION_CYCLE",
                        "/requirement_expressions",
                        "Expression cycle detected: " + " -> ".join(cycle),
                    )
                )
            return

        state[expression_id] = 1
        stack.append(expression_id)
        expression = expressions[expression_id]
        for member in expression.get("members", []):
            if member.get("kind") != "EXPRESSION":
                continue
            child_id = member.get("id")
            if isinstance(child_id, str) and child_id in expressions:
                visit(child_id)
        stack.pop()
        state[expression_id] = 2

    for expression_id in expressions:
        if state.get(expression_id, 0) == 0:
            visit(expression_id)
    return issues


def validate_report(
    report: Mapping[str, Any], schema_path: Path | None = None
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    for position, advisory in enumerate(report.get("advisories", [])):
        if not isinstance(advisory, Mapping):
            continue
        forbidden = {"verdict", "score_weight", "score_strength", "scoreable"}.intersection(advisory)
        if forbidden:
            issues.append(
                _issue(
                    "ADVISORY_MUST_NOT_BE_SCOREABLE",
                    f"/advisories/{position}",
                    "Advisories cannot carry verdict or scoring fields: "
                    + ", ".join(sorted(forbidden)),
                )
            )

    structural_issues = list(schema_issues(report, schema_path))
    issues.extend(structural_issues)
    if structural_issues:
        return tuple(issues)

    documents, duplicate_issues = _index_by_id(report["inputs"], "document_id")
    issues.extend(duplicate_issues)
    spans, duplicate_issues = _index_by_id(report["source_spans"], "span_id")
    issues.extend(duplicate_issues)
    criteria, duplicate_issues = _index_by_id(report["criteria"], "criterion_id")
    issues.extend(duplicate_issues)
    expressions, duplicate_issues = _index_by_id(
        report["requirement_expressions"], "expression_id"
    )
    issues.extend(duplicate_issues)
    evidence, duplicate_issues = _index_by_id(report["evidence"], "evidence_id")
    issues.extend(duplicate_issues)
    assessments, duplicate_issues = _index_by_id(report["assessments"], "assessment_id")
    issues.extend(duplicate_issues)
    integrity, duplicate_issues = _index_by_id(report["integrity_findings"], "finding_id")
    issues.extend(duplicate_issues)

    for position, document_id in enumerate(report["request"]["inputs"]):
        _require_reference(
            document_id,
            documents,
            f"/request/inputs/{position}",
            "document",
            issues,
        )

    for position, span in enumerate(report["source_spans"]):
        _require_reference(
            span["document_id"],
            documents,
            f"/source_spans/{position}/document_id",
            "document",
            issues,
        )

    for position, criterion in enumerate(report["criteria"]):
        valid_requirement_span = False
        for span_position, span_id in enumerate(criterion["original_spans"]):
            span = _require_reference(
                span_id,
                spans,
                f"/criteria/{position}/original_spans/{span_position}",
                "source span",
                issues,
            )
            if span is None:
                continue
            document = documents.get(span["document_id"])
            if document is not None and document["role"] == "REQUIREMENT_SOURCE":
                valid_requirement_span = True
        if not valid_requirement_span:
            issues.append(
                _issue(
                    "CRITERION_PROVENANCE_REQUIRED",
                    f"/criteria/{position}/original_spans",
                    "Criterion provenance must include a requirement-source span.",
                )
            )

        scope = criterion["artifact_scope"]
        for document_position, document_id in enumerate(scope["document_ids"]):
            document = _require_reference(
                document_id,
                documents,
                f"/criteria/{position}/artifact_scope/document_ids/{document_position}",
                "document",
                issues,
            )
            if document is not None and document["role"] != "ARTIFACT":
                issues.append(
                    _issue(
                        "ARTIFACT_SCOPE_VIOLATION",
                        f"/criteria/{position}/artifact_scope/document_ids/{document_position}",
                        f"Artifact scope references non-artifact document {document_id!r}.",
                    )
                )

    evidence_documents: dict[str, set[str]] = {}
    for position, item in enumerate(report["evidence"]):
        valid_artifact_span = False
        source_documents: set[str] = set()
        for span_position, span_id in enumerate(item["source_spans"]):
            span = _require_reference(
                span_id,
                spans,
                f"/evidence/{position}/source_spans/{span_position}",
                "source span",
                issues,
            )
            if span is None:
                continue
            source_documents.add(span["document_id"])
            document = documents.get(span["document_id"])
            if document is not None and document["role"] == "ARTIFACT":
                valid_artifact_span = True
        evidence_documents[item["evidence_id"]] = source_documents
        if not valid_artifact_span:
            issues.append(
                _issue(
                    "EVIDENCE_PROVENANCE_REQUIRED",
                    f"/evidence/{position}/source_spans",
                    "Evidence provenance must include an artifact span.",
                )
            )
        for criterion_position, criterion_id in enumerate(item["criterion_ids"]):
            _require_reference(
                criterion_id,
                criteria,
                f"/evidence/{position}/criterion_ids/{criterion_position}",
                "criterion",
                issues,
            )

    for position, expression in enumerate(report["requirement_expressions"]):
        for provenance_position, span_id in enumerate(expression["provenance"]):
            _require_reference(
                span_id,
                spans,
                f"/requirement_expressions/{position}/provenance/{provenance_position}",
                "source span",
                issues,
            )
        for member_position, member in enumerate(expression["members"]):
            target_index = criteria if member["kind"] == "CRITERION" else expressions
            target_label = "criterion" if member["kind"] == "CRITERION" else "expression"
            _require_reference(
                member["id"],
                target_index,
                f"/requirement_expressions/{position}/members/{member_position}/id",
                target_label,
                issues,
            )
    issues.extend(_detect_expression_cycles(expressions))

    for position, assessment in enumerate(report["assessments"]):
        criterion = _require_reference(
            assessment["criterion_id"],
            criteria,
            f"/assessments/{position}/criterion_id",
            "criterion",
            issues,
        )
        linked_evidence: list[Mapping[str, Any]] = []
        for evidence_position, evidence_id in enumerate(assessment["evidence_ids"]):
            item = _require_reference(
                evidence_id,
                evidence,
                f"/assessments/{position}/evidence_ids/{evidence_position}",
                "evidence",
                issues,
            )
            if item is not None:
                linked_evidence.append(item)
                if assessment["criterion_id"] not in item["criterion_ids"]:
                    issues.append(
                        _issue(
                            "EVIDENCE_CRITERION_MISMATCH",
                            f"/assessments/{position}/evidence_ids/{evidence_position}",
                            f"Evidence {evidence_id!r} is not linked to criterion "
                            f"{assessment['criterion_id']!r}.",
                        )
                    )

        verdict = assessment["verdict"]
        if verdict == "MET" and not linked_evidence:
            issues.append(
                _issue(
                    "MET_REQUIRES_EVIDENCE",
                    f"/assessments/{position}/evidence_ids",
                    "MET requires at least one evidence item.",
                )
            )
        if verdict == "PARTIAL" and not linked_evidence:
            issues.append(
                _issue(
                    "PARTIAL_REQUIRES_EVIDENCE",
                    f"/assessments/{position}/evidence_ids",
                    "PARTIAL requires at least one evidence item.",
                )
            )
        if verdict == "CONTRADICTED" and not linked_evidence:
            issues.append(
                _issue(
                    "CONTRADICTED_REQUIRES_EVIDENCE",
                    f"/assessments/{position}/evidence_ids",
                    "CONTRADICTED requires explicit conflicting evidence.",
                )
            )
        if verdict == "UNVERIFIABLE" and not assessment["uncertainty_notes"]:
            issues.append(
                _issue(
                    "UNVERIFIABLE_REQUIRES_LIMITATION",
                    f"/assessments/{position}/uncertainty_notes",
                    "UNVERIFIABLE requires a stated limiting condition.",
                )
            )
        if verdict == "MISSING" and not assessment["search_scope"]["complete"]:
            issues.append(
                _issue(
                    "MISSING_REQUIRES_COMPLETE_SEARCH_SCOPE",
                    f"/assessments/{position}/search_scope/complete",
                    "MISSING requires a complete search of the relevant artifact scope.",
                )
            )
        if (
            verdict == "MET"
            and linked_evidence
            and all(item["strength"] == "RELATED" for item in linked_evidence)
        ):
            issues.append(
                _issue(
                    "RELATED_CANNOT_SOLELY_SUPPORT_MET",
                    f"/assessments/{position}/evidence_ids",
                    "RELATED evidence alone cannot justify MET.",
                )
            )

        if criterion is not None:
            if (
                criterion["requirement_kind"] == "ABSENCE"
                and verdict == "MET"
                and not assessment["search_scope"]["complete"]
            ):
                issues.append(
                    _issue(
                        "ABSENCE_MET_REQUIRES_COMPLETE_SEARCH_SCOPE",
                        f"/assessments/{position}/search_scope/complete",
                        "An absence requirement can be MET only after complete relevant inspection.",
                    )
                )

            allowed_documents: set[str] | None = None
            scope = criterion["artifact_scope"]
            if scope["mode"] == "SPECIFIC_ARTIFACTS":
                allowed_documents = set(scope["document_ids"])
            if allowed_documents is not None:
                for item in linked_evidence:
                    disallowed = evidence_documents.get(item["evidence_id"], set()) - allowed_documents
                    if disallowed:
                        issues.append(
                            _issue(
                                "ARTIFACT_SCOPE_VIOLATION",
                                f"/assessments/{position}/evidence_ids",
                                "Evidence comes from artifact document(s) outside the criterion scope: "
                                + ", ".join(sorted(disallowed)),
                            )
                        )
                search_disallowed = set(assessment["search_scope"]["document_ids"]) - allowed_documents
                if search_disallowed:
                    issues.append(
                        _issue(
                            "ARTIFACT_SCOPE_VIOLATION",
                            f"/assessments/{position}/search_scope/document_ids",
                            "Search scope includes artifact document(s) outside the criterion scope: "
                            + ", ".join(sorted(search_disallowed)),
                        )
                    )

        for document_position, document_id in enumerate(assessment["search_scope"]["document_ids"]):
            document = _require_reference(
                document_id,
                documents,
                f"/assessments/{position}/search_scope/document_ids/{document_position}",
                "document",
                issues,
            )
            if document is not None and document["role"] != "ARTIFACT":
                issues.append(
                    _issue(
                        "ARTIFACT_SCOPE_VIOLATION",
                        f"/assessments/{position}/search_scope/document_ids/{document_position}",
                        f"Search scope references non-artifact document {document_id!r}.",
                    )
                )

        for impact_position, finding_id in enumerate(assessment["integrity_impacts"]):
            _require_reference(
                finding_id,
                integrity,
                f"/assessments/{position}/integrity_impacts/{impact_position}",
                "integrity finding",
                issues,
            )

    for position, result in enumerate(report["expression_results"]):
        _require_reference(
            result["expression_id"],
            expressions,
            f"/expression_results/{position}/expression_id",
            "expression",
            issues,
        )
        for member_position, assessment_id in enumerate(result["member_assessment_ids"]):
            _require_reference(
                assessment_id,
                assessments,
                f"/expression_results/{position}/member_assessment_ids/{member_position}",
                "assessment",
                issues,
            )

    return tuple(issues)


def assert_valid_report(
    report: Mapping[str, Any], schema_path: Path | None = None
) -> None:
    issues = validate_report(report, schema_path)
    if not issues:
        return
    message = "\n".join(f"[{issue.code}] {issue.path}: {issue.message}" for issue in issues)
    raise ValueError(message)
