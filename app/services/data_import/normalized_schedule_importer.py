from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from .schedule_importer import import_schedule_excel
from .schedule_normalizer import normalize_schedule_excel

CANONICAL_COLUMNS = [
    "activity_code",
    "activity_name",
    "wbs_id",
    "duration_days",
    "progress_percent",
    "status",
    "start_date",
    "finish_date",
    "responsible_party",
]


def _build_canonical_dataframe(
    normalized_rows: list[dict[str, Any]],
) -> pd.DataFrame:

    dataframe = pd.DataFrame(normalized_rows)

    for column in CANONICAL_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = None

    return dataframe[CANONICAL_COLUMNS]


def normalize_and_import_schedule_excel(
    db: Session,
    file_path: str,
    project_id: int,
) -> dict[str, Any]:

    source_path = Path(file_path)

    if not source_path.exists():
        raise FileNotFoundError(str(source_path))

    normalization = normalize_schedule_excel(source_path)

    if normalization.status in (
        "needs_user_input",
        "needs_review",
    ):
        return {
            "status": normalization.status,
            "project_id": project_id,
            "source_file": source_path.name,
            "normalization": normalization,
            "imported": False,
        }

    if normalization.status != "ready":
        raise ValueError(
            f"Unsupported normalization status: "
            f"{normalization.status}"
        )

    if not normalization.normalized_rows:
        raise ValueError(
            "Normalization returned ready status "
            "without normalized rows."
        )

    canonical_df = _build_canonical_dataframe(
        normalization.normalized_rows
    )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            prefix="pip_normalized_",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        canonical_df.to_excel(
            temp_path,
            index=False,
            sheet_name="Schedule",
        )

        importer_result = import_schedule_excel(
            db=db,
            file_path=str(temp_path),
            project_id=project_id,
        )

        return {
            "status": "completed",
            "project_id": project_id,
            "source_file": source_path.name,
            "normalization_status": normalization.status,
            "normalized_row_count": len(
                normalization.normalized_rows
            ),
            "importer": importer_result,
            "imported": True,
        }

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
