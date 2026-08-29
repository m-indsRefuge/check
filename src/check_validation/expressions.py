from collections.abc import Mapping
from typing import Any


def _criterion_strength(criterion: Mapping[str, Any]) -> str | None:
    strength = criterion["strength"]
    if strength == "CONDITIONAL":
        if criterion["applicability"] != "APPLIES":
            return None
        return criterion.get("effective_strength_if_applies") or "UNSPECIFIED"
    return strength


def _merge_strengths(strengths: list[str | None]) -> str | None:
    present = [strength for strength in strengths if strength is not None]
    if not present:
        return None
    unique = set(present)
    if len(unique) == 1:
        return present[0]
    if "REQUIRED" in unique:
        return "REQUIRED"
    if "PREFERRED" in unique:
        return "PREFERRED"
    return "UNSPECIFIED"


def _derive_verdict(operator: str, verdicts: list[str], minimum: int | None) -> tuple[str, str]:
    if not verdicts:
        return "UNVERIFIABLE", "No applicable members remain for evaluation."

    if operator == "SINGLE":
        return verdicts[0], "The single member determines the expression result."

    if operator == "ALL_OF":
        if all(verdict == "MET" for verdict in verdicts):
            return "MET", "All required members are fully satisfied."
        if any(verdict == "CONTRADICTED" for verdict in verdicts):
            return "CONTRADICTED", "At least one required member is explicitly contradicted."
        if any(verdict in {"MET", "PARTIAL"} for verdict in verdicts):
            return "PARTIAL", "Some required members have meaningful coverage, but the full obligation is not met."
        if any(verdict == "MISSING" for verdict in verdicts):
            return "MISSING", "No member provides enough coverage to satisfy the full obligation."
        return "UNVERIFIABLE", "The obligation cannot be evaluated reliably from the available members."

    if operator == "ANY_OF":
        if any(verdict == "MET" for verdict in verdicts):
            return "MET", "At least one permitted alternative is fully satisfied."
        if any(verdict == "PARTIAL" for verdict in verdicts):
            return "PARTIAL", "At least one permitted alternative has meaningful but incomplete coverage."
        if any(verdict == "UNVERIFIABLE" for verdict in verdicts):
            return "UNVERIFIABLE", "An unresolved alternative could change whether the obligation is satisfied."
        if all(verdict == "CONTRADICTED" for verdict in verdicts):
            return "CONTRADICTED", "All permitted alternatives are explicitly contradicted."
        return "MISSING", "None of the permitted alternatives is satisfied."

    if operator == "AT_LEAST_N_OF":
        if minimum is None:
            raise ValueError("AT_LEAST_N_OF requires minimum_satisfied")
        met = verdicts.count("MET")
        partial = verdicts.count("PARTIAL")
        unknown = verdicts.count("UNVERIFIABLE")
        if met >= minimum:
            return "MET", f"At least {minimum} members are fully satisfied."
        if met + partial >= minimum:
            return "PARTIAL", f"Partial coverage could complete the required {minimum} satisfied members."
        if met + partial + unknown >= minimum:
            return "UNVERIFIABLE", f"Unknown members could change whether {minimum} members are satisfied."
        remaining = [verdict for verdict in verdicts if verdict != "MET"]
        if remaining and all(verdict == "CONTRADICTED" for verdict in remaining):
            return "CONTRADICTED", "All remaining paths needed to reach the threshold are contradicted."
        return "MISSING", f"Fewer than {minimum} members are satisfied."

    raise ValueError(f"Unsupported expression operator: {operator}")


def derive_expression_results(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    criteria = {item["criterion_id"]: item for item in report["criteria"]}
    assessments_by_criterion = {
        item["criterion_id"]: item for item in report["assessments"]
    }
    expressions = {
        item["expression_id"]: item for item in report["requirement_expressions"]
    }
    source_order = [item["expression_id"] for item in report["requirement_expressions"]]

    conflicted_criteria: set[str] = set()
    conflicted_expressions: set[str] = set()
    for conflict in report.get("source_conflicts", []):
        if conflict.get("resolved"):
            continue
        conflicted_criteria.update(conflict.get("affected_criterion_ids", []))
        conflicted_expressions.update(conflict.get("affected_expression_ids", []))

    cache: dict[str, dict[str, Any]] = {}
    resolving: set[str] = set()

    def criterion_state(criterion_id: str) -> dict[str, Any]:
        criterion = criteria[criterion_id]
        assessment = assessments_by_criterion[criterion_id]
        applicability = criterion["applicability"]
        if criterion_id in conflicted_criteria:
            verdict = "UNVERIFIABLE"
            excluded_reason = "SOURCE_CONFLICT"
        elif applicability == "DOES_NOT_APPLY":
            verdict = "UNVERIFIABLE"
            excluded_reason = "DOES_NOT_APPLY"
        elif applicability == "APPLICABILITY_UNKNOWN":
            verdict = "UNVERIFIABLE"
            excluded_reason = "APPLICABILITY_UNKNOWN"
        else:
            verdict = assessment["verdict"]
            excluded_reason = None
        return {
            "verdict": verdict,
            "assessment_ids": [assessment["assessment_id"]],
            "score_strength": _criterion_strength(criterion),
            "excluded_reason": excluded_reason,
        }

    def resolve(expression_id: str) -> dict[str, Any]:
        if expression_id in cache:
            return cache[expression_id]
        if expression_id in resolving:
            raise ValueError(f"Expression cycle detected at {expression_id}")
        resolving.add(expression_id)

        expression = expressions[expression_id]
        member_states: list[dict[str, Any]] = []
        for member in expression["members"]:
            if member["kind"] == "CRITERION":
                member_states.append(criterion_state(member["id"]))
            else:
                child = resolve(member["id"])
                member_states.append(
                    {
                        "verdict": child["verdict"],
                        "assessment_ids": child["member_assessment_ids"],
                        "score_strength": child["score_strength"],
                        "excluded_reason": child["excluded_reason"],
                    }
                )

        assessment_ids = list(
            dict.fromkeys(
                assessment_id
                for state in member_states
                for assessment_id in state["assessment_ids"]
            )
        )
        strengths = [state["score_strength"] for state in member_states]

        if expression_id in conflicted_expressions:
            verdict = "UNVERIFIABLE"
            reasoning = "The expression is affected by an unresolved source conflict."
            excluded_reason = "SOURCE_CONFLICT"
        else:
            active_states = [
                state for state in member_states if state["excluded_reason"] != "DOES_NOT_APPLY"
            ]
            verdicts = [state["verdict"] for state in active_states]
            verdict, reasoning = _derive_verdict(
                expression["operator"], verdicts, expression.get("minimum_satisfied")
            )
            if not active_states and member_states:
                excluded_reason = "DOES_NOT_APPLY"
            elif expression["operator"] == "SINGLE" and len(member_states) == 1:
                excluded_reason = member_states[0]["excluded_reason"]
            elif verdict == "UNVERIFIABLE":
                reasons = {
                    state["excluded_reason"]
                    for state in active_states
                    if state["excluded_reason"] is not None
                }
                excluded_reason = next(iter(reasons)) if len(reasons) == 1 else None
            else:
                excluded_reason = None

        result = {
            "expression_id": expression_id,
            "verdict": verdict,
            "member_assessment_ids": assessment_ids,
            "reasoning": reasoning,
            "score_strength": _merge_strengths(strengths),
            "excluded_reason": excluded_reason,
        }
        cache[expression_id] = result
        resolving.remove(expression_id)
        return result

    for expression_id in source_order:
        resolve(expression_id)
    return [cache[expression_id] for expression_id in source_order]
