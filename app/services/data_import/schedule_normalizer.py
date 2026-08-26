from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.ai.smart_import_agent import (
    resolve_column_mapping,
)

from .column_mapper import map_columns
from .normalization_models import (
    ColumnMapping,
    MissingField,
    NormalizationResult,
)
from .schedule_contract import (
    REQUIRED_FIELDS,
    SCHEDULE_CONTRACT,
)


def _clean_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    value = str(value).strip()

    return value or None


def _clean_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None

    try:
        value = str(value).strip().replace("%", "")
        result = float(value)

        if 0 <= result <= 1 and "%" not in str(value):
            result *= 100

        return result
    except (TypeError, ValueError):
        return None


def _clean_date(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None

    try:
        return pd.to_datetime(value).to_pydatetime()
    except Exception:
        return None


def _convert(value: Any, field: str) -> Any:
    field_type = SCHEDULE_CONTRACT[field]["type"]

    if field_type == "string":
        return _clean_string(value)

    if field_type == "integer":
        return _clean_int(value)

    if field_type == "float":
        return _clean_float(value)

    if field_type == "date":
        return _clean_date(value)

    return value


def normalize_schedule_excel(
    file_path: str | Path,
) -> NormalizationResult:

    file_path = Path(file_path)

    workbook = pd.ExcelFile(file_path)

    if not workbook.sheet_names:
        raise ValueError("Excel workbook contains no sheets.")

    # Initial strategy:
    # select the first non-empty worksheet.
    selected_sheet = None
    df = None

    for sheet_name in workbook.sheet_names:
        candidate = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
        )

        if len(candidate.columns) > 0 and len(candidate) > 0:
            selected_sheet = sheet_name
            df = candidate
            break

    if df is None:
        raise ValueError("No usable worksheet found.")

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    mappings = map_columns(
        list(df.columns)
    )

    # ========================================================
    # SMART IMPORT AGENT
    #
    # Deterministic mapping remains the first authority.
    #
    # Only fuzzy_review mappings are sent to AI.
    #
    # AI ACCEPT:
    #     fuzzy_review -> ai_semantic_validation
    #
    # AI UNCERTAIN / TIMEOUT:
    #     target_field -> None
    #     method -> ai_review_required
    #
    # This guarantees that uncertain mappings cannot silently
    # reach the database importer.
    # ========================================================

    ai_review_required = False
    ai_review_questions: list[dict[str, Any]] = []

    resolved_mappings: list[ColumnMapping] = []

    for mapping in mappings:

        if mapping.method != "fuzzy_review":

            resolved_mappings.append(mapping)
            continue

        source_column = str(
            mapping.source_column or ""
        ).strip()

        candidate_target = (
            str(mapping.target_field).strip()
            if mapping.target_field
            else None
        )

        sample_values = []

        try:
            for value in (
                df[source_column].dropna().head(8).tolist()
                if source_column in df.columns
                else []
            ):
                sample_values.append(value)
        except Exception:
            sample_values = []

        try:

            ai_result = resolve_column_mapping(
                source_column=source_column,
                candidate_target=candidate_target,
                confidence=mapping.confidence,
                reason=mapping.reason,
                sample_values=sample_values,
                all_columns=list(df.columns),
            )

        except Exception as exc:

            ai_result = {
                "decision": "ask_user",
                "target": None,
                "confidence": 0.0,
                "reason": (
                    "Smart Import Agent execution failed."
                ),
                "question": (
                    f"ستون '{source_column}' "
                    "مربوط به کدام فیلد پروژه است؟"
                ),
                "ai_status": "fallback",
                "ai_error": str(exc),
            }

        if (
            ai_result.get("decision") == "accept"
            and ai_result.get("target")
            and ai_result.get("confidence", 0.0) >= 0.90
        ):

            resolved_mappings.append(
                ColumnMapping(
                    source_column=source_column,
                    target_field=ai_result["target"],
                    confidence=float(
                        ai_result["confidence"]
                    ),
                    method="ai_semantic_validation",
                    reason=str(
                        ai_result.get(
                            "reason",
                            "AI semantic validation passed.",
                        )
                    ),
                )
            )

        else:

            ai_review_required = True

            ai_review_questions.append({
                "source": source_column,
                "target_candidate": candidate_target,
                "confidence": ai_result.get(
                    "confidence",
                    0.0,
                ),
                "reason": ai_result.get(
                    "reason",
                    "Candidate mapping requires user confirmation.",
                ),
                "question": ai_result.get(
                    "question",
                    (
                        f"ستون '{source_column}' "
                        "مربوط به کدام فیلد پروژه است؟"
                    ),
                ),
                "ai_status": ai_result.get(
                    "ai_status",
                    "fallback",
                ),
            })

            # IMPORTANT:
            # Do NOT preserve the fuzzy candidate.
            #
            # An uncertain candidate must not participate in
            # target_to_source and must not generate normalized
            # database-ready rows.
            resolved_mappings.append(
                ColumnMapping(
                    source_column=source_column,
                    target_field=None,
                    confidence=0.0,
                    method="ai_review_required",
                    reason=str(
                        ai_result.get(
                            "reason",
                            "AI mapping requires user confirmation.",
                        )
                    ),
                )
            )

    mappings = resolved_mappings

    target_to_source: dict[str, ColumnMapping] = {}

    warnings: list[str] = []

    for mapping in mappings:

        if mapping.target_field is None:
            warnings.append(
                f"Unmapped source column: {mapping.source_column}"
            )
            continue

        existing = target_to_source.get(
            mapping.target_field
        )

        if existing is None:
            target_to_source[
                mapping.target_field
            ] = mapping

        elif mapping.confidence > existing.confidence:
            warnings.append(
                f"Duplicate mapping for {mapping.target_field}; "
                f"selected {mapping.source_column}."
            )

            target_to_source[
                mapping.target_field
            ] = mapping

    missing_fields: list[MissingField] = []

    for field in REQUIRED_FIELDS:

        if field not in target_to_source:
            missing_fields.append(
                MissingField(
                    field=field,
                    required=True,
                    reason=(
                        "Required canonical field could not "
                        "be mapped from the uploaded workbook."
                    ),
                    can_infer=False,
                )
            )

    normalized_rows: list[dict[str, Any]] = []

    if not missing_fields:

        for _, row in df.iterrows():

            normalized = {}

            for field, mapping in target_to_source.items():

                source_value = row.get(
                    mapping.source_column
                )

                normalized[field] = _convert(
                    source_value,
                    field,
                )

            normalized_rows.append(
                normalized
            )

    requires_review = any(
        mapping.method == "fuzzy_review"
        for mapping in mappings
    )

    if missing_fields or ai_review_required:
        status = "needs_user_input"

    elif requires_review:
        status = "needs_review"

    else:
        status = "ready"

    # ============================================================
    # EXCEL_HANDLE_RELEASE
    #
    # pandas.ExcelFile keeps the workbook/file handle open.
    # The API removes the uploaded temporary file in its finally
    # block, so the workbook MUST be explicitly closed first.
    # ============================================================
    with contextlib.suppress(Exception):
        workbook.close()

    return NormalizationResult(
        status=status,
        mappings=mappings,
        missing_fields=missing_fields,
        warnings=warnings,
        normalized_rows=normalized_rows,
        metadata={
            "file_name": file_path.name,
            "sheet": selected_sheet,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "smart_import_agent": {
                "enabled": True,
                "review_required": ai_review_required,
                "questions": ai_review_questions,
            },
        },
    )


