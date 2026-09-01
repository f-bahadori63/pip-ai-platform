from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.cost.cost import ProjectCost
from app.models.schedule import ScheduleActivity
from app.services.data_import.schedule_normalizer import (
    normalize_schedule_excel,
)
from app.services.wbs_import_service import (
    replace_project_wbs_from_schedule,
)

# Canonical financial fields that, when present in the uploaded
# workbook, trigger automatic project-cost aggregation.
COST_FIELDS = ("budgeted_cost", "actual_cost", "earned_value")


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

    # Which of the optional cost fields were actually mapped from a
    # column in this workbook (as opposed to being absent entirely).
    mapped_cost_fields = {
        mapping.target_field
        for mapping in result.mappings
        if mapping.target_field in COST_FIELDS
    }

    cost_data_detected = bool(mapped_cost_fields)

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
                    # The workbook's WBS value is a source code, not a
                    # database foreign key. It is resolved after all rows are
                    # imported and the old project WBS has been replaced.
                    wbs_id=None,
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
                    budgeted_cost=row.get("budgeted_cost"),
                    actual_cost=row.get("actual_cost"),
                    earned_value=row.get("earned_value"),
                )

                db.add(activity)
                created_count += 1

            else:

                activity.activity_name = activity_name
                # Re-linked to the new project-scoped WBS below.
                activity.wbs_id = None
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
                activity.budgeted_cost = row.get("budgeted_cost")
                activity.actual_cost = row.get("actual_cost")
                activity.earned_value = row.get("earned_value")

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

        removed_count = 0

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

            removed_count = stale_query.delete(
                synchronize_session=False
            )

        db.flush()

        # SOURCE OF TRUTH: a successful upload replaces the selected
        # project's previous WBS. The new WBS is built from wbs_code /
        # wbs_name in this workbook, with deterministic activity-code
        # derivation as a fallback.
        wbs_result = replace_project_wbs_from_schedule(
            db=db,
            project_id=project_id,
            normalized_rows=result.normalized_rows,
        )

        # ============================================================
        # AUTOMATIC COST AGGREGATION
        # ============================================================
        # If the uploaded workbook contained cost-loaded-schedule
        # columns (budgeted_cost / actual_cost / earned_value), sum
        # them across every currently-imported activity and upsert a
        # single ProjectCost row tagged source="schedule_import".
        #
        # This row is idempotent: each successful upload with cost
        # data REPLACES the previous auto-detected snapshot, it does
        # not accumulate. Manually entered cost rows (source="manual")
        # are never touched by this step.
        # ============================================================

        cost_summary = None

        if cost_data_detected:

            total_budgeted = sum(
                (row.get("budgeted_cost") or 0)
                for row in result.normalized_rows
            )

            total_actual = sum(
                (row.get("actual_cost") or 0)
                for row in result.normalized_rows
            )

            total_earned = sum(
                (row.get("earned_value") or 0)
                for row in result.normalized_rows
            )

            auto_cost_row = (
                db.query(ProjectCost)
                .filter(
                    ProjectCost.project_id == project_id,
                    ProjectCost.source == "schedule_import",
                )
                .first()
            )

            if auto_cost_row is None:
                auto_cost_row = ProjectCost(
                    project_id=project_id,
                    source="schedule_import",
                )
                db.add(auto_cost_row)

            auto_cost_row.planned_cost = total_budgeted
            auto_cost_row.actual_cost = total_actual
            auto_cost_row.earned_value = total_earned

            cost_summary = {
                "detected_fields": sorted(mapped_cost_fields),
                "planned_cost": total_budgeted,
                "actual_cost": total_actual,
                "earned_value": total_earned,
            }

        db.commit()

        return {
            "project_id": project_id,
            "imported_count": imported_count,
            "created_count": created_count,
            "updated_count": updated_count,
            "removed_count": int(removed_count or 0),
            "status": "completed",
            "imported": True,
            "normalization_status": "ready",
            "normalized_row_count": len(
                result.normalized_rows
            ),
            "wbs": wbs_result,
            "cost_auto_detected": cost_data_detected,
            "cost_summary": cost_summary,
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
