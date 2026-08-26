from __future__ import annotations

import pandas as pd

from sqlalchemy.orm import Session

from app.models.schedule import ScheduleActivity
from app.services.data_import.schedule_normalizer import (
    normalize_schedule_excel,
)


def import_schedule_excel(
    db: Session,
    file_path: str,
    project_id: int,
):
    """
    Smart Excel import gate.

    Pipeline:
        Excel
          -> Smart Normalizer
          -> READY
          -> Idempotent Upsert
          -> PostgreSQL

    Normalization failures never modify the database.
    """

    result = normalize_schedule_excel(file_path)

    if result.status != "ready":
        return {
            "project_id": project_id,
            "status": result.status,
            "imported": False,
            "normalization": {
                "status": result.status,
                "mappings": [
                    {
                        "source_column": m.source_column,
                        "target_field": m.target_field,
                        "confidence": m.confidence,
                        "method": m.method,
                        "reason": m.reason,
                    }
                    for m in result.mappings
                ],
                "missing_fields": [
                    {
                        "field": f.field,
                        "required": f.required,
                        "reason": f.reason,
                        "can_infer": f.can_infer,
                    }
                    for f in result.missing_fields
                ],
                "warnings": result.warnings,
                "metadata": result.metadata,
            },
        }

    created_count = 0
    updated_count = 0
    imported_count = 0

    try:
        for index, row in enumerate(result.normalized_rows):

            activity_code = row.get("activity_code")
            activity_name = row.get("activity_name")

            if not activity_code:
                raise ValueError(
                    f"Normalized row {index + 1}: "
                    "activity_code is required"
                )

            if not activity_name:
                raise ValueError(
                    f"Normalized row {index + 1}: "
                    "activity_name is required"
                )

            activity = (
                db.query(ScheduleActivity)
                .filter(
                    ScheduleActivity.project_id == project_id,
                    ScheduleActivity.activity_code == activity_code,
                )
                .first()
            )

            if activity is None:

                activity = ScheduleActivity(
                    project_id=project_id,
                    activity_code=activity_code,
                    activity_name=activity_name,
                    wbs_id=row.get("wbs_id"),
                    duration_days=row.get("duration_days"),
                    progress_percent=(
                        row.get("progress_percent")
                        if row.get("progress_percent") is not None
                        else 0
                    ),
                    status=(
                        row.get("status")
                        if row.get("status")
                        else "Not Started"
                    ),
                    start_date=row.get("start_date"),
                    finish_date=row.get("finish_date"),
                    responsible_party=row.get(
                        "responsible_party"
                    ),
                )

                db.add(activity)
                created_count += 1

            else:

                activity.activity_name = activity_name
                activity.wbs_id = row.get("wbs_id")
                activity.duration_days = row.get(
                    "duration_days"
                )
                activity.progress_percent = (
                    row.get("progress_percent")
                    if row.get("progress_percent") is not None
                    else 0
                )
                activity.status = (
                    row.get("status")
                    if row.get("status")
                    else "Not Started"
                )
                activity.start_date = row.get("start_date")
                activity.finish_date = row.get(
                    "finish_date"
                )
                activity.responsible_party = row.get(
                    "responsible_party"
                )

                updated_count += 1

            imported_count += 1

        # ============================================================
        # SOURCE_OF_TRUTH_CLEANUP
        # ============================================================
        # The uploaded Excel file is the authoritative current
        # schedule for this project.
        #
        # Existing activities that are NOT present in the uploaded
        # schedule must therefore be removed.
        #
        # This runs inside the same SQLAlchemy transaction as the
        # insert/update operations above. If anything fails before
        # commit(), the transaction is rolled back.
        # ============================================================

        incoming_activity_codes = {
            str(row.get("activity_code")).strip()
            for row in result.normalized_rows
            if row.get("activity_code") is not None
            and str(row.get("activity_code")).strip()
        }

        if incoming_activity_codes:
            stale_query = (
                db.query(ScheduleActivity)
                .filter(
                    ScheduleActivity.project_id == project_id,
                    ~ScheduleActivity.activity_code.in_(
                        incoming_activity_codes
                    ),
                )
            )

            stale_deleted_count = stale_query.delete(
                synchronize_session=False
            )
        else:
            stale_deleted_count = 0

        db.commit()

        return {
            "project_id": project_id,
            "imported_count": imported_count,
            "created_count": created_count,
            "updated_count": updated_count,
            "status": "completed",
            "imported": True,
            "normalization_status": "ready",
            "normalized_row_count": len(
                result.normalized_rows
            ),
        }

    except Exception:
        db.rollback()
        raise


def normalize_and_import_schedule_excel(
    db: Session,
    file_path: str,
    project_id: int,
):
    """
    Public normalization/import gate used by API routes.
    """

    return import_schedule_excel(
        db=db,
        file_path=file_path,
        project_id=project_id,
    )

