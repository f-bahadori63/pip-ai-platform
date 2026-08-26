from __future__ import annotations

import re
from difflib import SequenceMatcher

from .normalization_models import ColumnMapping
from .schedule_contract import SCHEDULE_CONTRACT


def normalize_column_name(value: str) -> str:
    value = str(value).strip().lower()

    value = value.replace("%", " percent ")
    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = value.replace("/", " ")
    value = value.replace("\\", " ")

    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _tokens(value: str) -> set[str]:
    return set(normalize_column_name(value).split())


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(
        None,
        normalize_column_name(left),
        normalize_column_name(right),
    ).ratio()


def _semantic_score(
    source_column: str,
    target: str,
) -> float:
    definition = SCHEDULE_CONTRACT[target]

    source = normalize_column_name(source_column)
    source_tokens = _tokens(source)

    score = 0.0

    positive_terms = {
        normalize_column_name(term)
        for term in definition.get("positive_terms", [])
    }

    negative_terms = {
        normalize_column_name(term)
        for term in definition.get("negative_terms", [])
    }

    for term in positive_terms:
        if term in source_tokens:
            score += 0.18
        elif term and term in source:
            score += 0.08

    for term in negative_terms:
        if term in source_tokens:
            score -= 0.24
        elif term and term in source:
            score -= 0.10

    # Strong semantic guards.
    if target == "activity_name":
        if any(
            token in source_tokens
            for token in {
                "title",
                "description",
                "desc",
                "name",
                "scope",
            }
        ):
            score += 0.55

        if any(
            token in source_tokens
            for token in {
                "code",
                "id",
                "identifier",
                "number",
                "no",
            }
        ):
            score -= 0.70

    if target == "activity_code":
        if any(
            token in source_tokens
            for token in {
                "title",
                "description",
                "desc",
                "name",
                "scope",
            }
        ):
            score -= 0.80

        if any(
            token in source_tokens
            for token in {
                "code",
                "id",
                "identifier",
                "number",
                "no",
            }
        ):
            score += 0.60

    if target == "start_date":
        if "start" in source_tokens or "begin" in source_tokens:
            score += 0.45

        if "finish" in source_tokens or "end" in source_tokens:
            score -= 0.65

    if target == "finish_date":
        if "finish" in source_tokens or "end" in source_tokens:
            score += 0.45

        if "start" in source_tokens or "begin" in source_tokens:
            score -= 0.65

    if target == "duration_days":
        if "duration" in source_tokens:
            score += 0.50

        if "date" in source_tokens:
            score -= 0.45

    if target == "progress_percent" and (
        "progress" in source_tokens
        or "complete" in source_tokens
        or "completion" in source_tokens
    ):
        score += 0.45

    if target == "status" and (
        "status" in source_tokens or "state" in source_tokens
    ):
        score += 0.55

    if target == "responsible_party" and any(
        token in source_tokens
        for token in {
            "responsible",
            "contractor",
            "subcontractor",
            "company",
            "discipline",
            "owner",
            "assigned",
            "party",
        }
    ):
        score += 0.55

    return score


SMART_EXCEL_ALIASES = {
    "discription": "activity_name",
    "description": "activity_name",
    "activity description": "activity_name",

    "wbs cod": "wbs_id",
    "wbs code": "wbs_id",
    "wbs id": "wbs_id",
    "wbs number": "wbs_id",

    "duration days": "duration_days",
    "duration day": "duration_days",
    "duration/days": "duration_days",
}
def _alias_match(
    source_column: str,
) -> tuple[str, str] | None:
    normalized_source = normalize_column_name(source_column)

    # --------------------------------------------------------
    # Deterministic smart Excel aliases
    # --------------------------------------------------------
    smart_target = SMART_EXCEL_ALIASES.get(
        normalized_source
    )

    if smart_target is not None:
        return (
            smart_target,
            f"Matched smart Excel alias '{source_column}'",
        )

    for target, _definition in SCHEDULE_CONTRACT.items():
        if normalized_source == normalize_column_name(target):
            return target, "Exact canonical field match"

    for target, definition in SCHEDULE_CONTRACT.items():
        for alias in definition["aliases"]:
            if normalized_source == normalize_column_name(alias):
                return target, f"Matched alias '{alias}'"

    return None


def _build_fuzzy_candidates(
    source_column: str,
) -> list[tuple[float, str]]:
    candidates: list[tuple[float, str]] = []

    for target, definition in SCHEDULE_CONTRACT.items():

        names = [target] + definition["aliases"]

        lexical_score = max(
            _similarity(source_column, candidate)
            for candidate in names
        )

        semantic_score = _semantic_score(
            source_column,
            target,
        )

        # Semantic information is deliberately weighted strongly
        # enough to prevent misleading lexical matches.
        combined = (
            lexical_score * 0.65
            + max(0.0, min(1.0, 0.5 + semantic_score)) * 0.35
        )

        # Explicit hard rejection for obvious semantic contradictions.
        source_tokens = _tokens(source_column)

        if target == "activity_code" and (
            source_tokens
            & {
                "title",
                "description",
                "desc",
                "scope",
            }
        ):
            combined -= 0.35

        if target == "activity_name" and (
            source_tokens
            & {
                "code",
                "id",
                "identifier",
                "number",
                "no",
            }
        ):
            combined -= 0.35

        candidates.append(
            (
                max(0.0, min(1.0, combined)),
                target,
            )
        )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates


def map_column(
    source_column: str,
) -> ColumnMapping:

    source_column = str(source_column).strip()

    # --------------------------------------------------------
    # 1. Exact / alias matching always wins.
    # --------------------------------------------------------
    alias_result = _alias_match(source_column)

    if alias_result is not None:
        target, reason = alias_result

        normalized_source = normalize_column_name(
            source_column
        )

        normalized_target = normalize_column_name(
            target
        )

        method = (
            "exact"
            if normalized_source == normalized_target
            else "alias"
        )

        confidence = 1.0 if method == "exact" else 0.97

        return ColumnMapping(
            source_column=source_column,
            target_field=target,
            confidence=confidence,
            method=method,
            reason=reason,
        )

    # --------------------------------------------------------
    # 2. Semantic + lexical fuzzy matching.
    # --------------------------------------------------------
    candidates = _build_fuzzy_candidates(
        source_column
    )

    if not candidates:
        return ColumnMapping(
            source_column=source_column,
            target_field=None,
            confidence=0.0,
            method="unmapped",
            reason="No candidate mapping found",
        )

    best_score, best_target = candidates[0]

    second_score = (
        candidates[1][0]
        if len(candidates) > 1
        else 0.0
    )

    margin = best_score - second_score

    # High confidence only when the winner is clearly separated.
    if best_score >= 0.90 and margin >= 0.08:
        return ColumnMapping(
            source_column=source_column,
            target_field=best_target,
            confidence=round(best_score, 4),
            method="semantic_fuzzy",
            reason="High-confidence semantic/lexical match",
        )

    # Review zone.
    if best_score >= 0.72 and margin >= 0.04:
        return ColumnMapping(
            source_column=source_column,
            target_field=best_target,
            confidence=round(best_score, 4),
            method="fuzzy_review",
            reason=(
                "Semantic fuzzy match is plausible "
                "but requires review"
            ),
        )

    # Conservative fallback.
    return ColumnMapping(
        source_column=source_column,
        target_field=None,
        confidence=round(best_score, 4),
        method="unmapped",
        reason=(
            "No sufficiently reliable semantic mapping found"
        ),
    )


def map_columns(
    source_columns: list[str],
) -> list[ColumnMapping]:

    mappings: list[ColumnMapping] = []

    # --------------------------------------------------------
    # Pass 1: exact + aliases.
    # This guarantees that strong mappings reserve targets.
    # --------------------------------------------------------
    reserved_targets: dict[str, ColumnMapping] = {}

    pending: list[str] = []

    for column in source_columns:

        mapping = map_column(column)

        if mapping.method in {
            "exact",
            "alias",
        }:
            if mapping.target_field not in reserved_targets:
                reserved_targets[
                    mapping.target_field
                ] = mapping
                mappings.append(mapping)
            else:
                mappings.append(
                    ColumnMapping(
                        source_column=column,
                        target_field=None,
                        confidence=0.0,
                        method="duplicate",
                        reason=(
                            f"Target field "
                            f"'{mapping.target_field}' "
                            "is already mapped by a stronger "
                            "source column."
                        ),
                    )
                )
        else:
            pending.append(column)

    # --------------------------------------------------------
    # Pass 2: fuzzy mapping only against unreserved targets.
    # --------------------------------------------------------
    for column in pending:

        candidates = _build_fuzzy_candidates(column)

        available = [
            item
            for item in candidates
            if item[1] not in reserved_targets
        ]

        if not available:
            mappings.append(
                ColumnMapping(
                    source_column=column,
                    target_field=None,
                    confidence=0.0,
                    method="unmapped",
                    reason=(
                        "No available target field remains "
                        "for this source column."
                    ),
                )
            )
            continue

        best_score, best_target = available[0]

        second_score = (
            available[1][0]
            if len(available) > 1
            else 0.0
        )

        margin = best_score - second_score

        if best_score >= 0.90 and margin >= 0.08:
            mapping = ColumnMapping(
                source_column=column,
                target_field=best_target,
                confidence=round(best_score, 4),
                method="semantic_fuzzy",
                reason=(
                    "High-confidence semantic/lexical "
                    "match after collision filtering"
                ),
            )

        elif best_score >= 0.72 and margin >= 0.04:
            mapping = ColumnMapping(
                source_column=column,
                target_field=best_target,
                confidence=round(best_score, 4),
                method="fuzzy_review",
                reason=(
                    "Ambiguous semantic fuzzy match "
                    "requires review"
                ),
            )

        else:
            mapping = ColumnMapping(
                source_column=column,
                target_field=None,
                confidence=round(best_score, 4),
                method="unmapped",
                reason=(
                    "No sufficiently reliable semantic "
                    "mapping found"
                ),
            )

        mappings.append(mapping)

        if (
            mapping.target_field is not None
            and mapping.method != "unmapped"
        ):
            reserved_targets[
                mapping.target_field
            ] = mapping

    # Preserve source-column order.
    by_source = {
        mapping.source_column: mapping
        for mapping in mappings
    }

    return [
        by_source[column]
        for column in source_columns
    ]

