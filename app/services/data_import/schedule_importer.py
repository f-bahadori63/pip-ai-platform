import pandas as pd

from sqlalchemy.orm import Session

from app.models.schedule import ScheduleActivity


REQUIRED_COLUMNS = [
    "activity_code",
    "activity_name",
]

OPTIONAL_COLUMNS = [
    "wbs_id",
    "duration_days",
    "progress_percent",
    "status",
    "start_date",
    "finish_date",
    "responsible_party",
]


def _clean_string(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _clean_int(value):
    if pd.isna(value):
        return None

    return int(float(value))


def _clean_float(value, default=0):
    if pd.isna(value):
        return default

    return float(value)


def _clean_date(value):
    if pd.isna(value):
        return None

    return pd.to_datetime(value).to_pydatetime()


def import_schedule_excel(
    db: Session,
    file_path: str,
    project_id: int,
):
    df = pd.read_excel(file_path)

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(missing_columns)
        )

    imported = []
    created_count = 0
    updated_count = 0

    for index, row in df.iterrows():

        activity_code = _clean_string(
            row["activity_code"]
        )

        activity_name = _clean_string(
            row["activity_name"]
        )

        if not activity_code:
            raise ValueError(
                f"Row {index + 2}: activity_code is required"
            )

        if not activity_name:
            raise ValueError(
                f"Row {index + 2}: activity_name is required"
            )

        wbs_id = (
            _clean_int(row["wbs_id"])
            if "wbs_id" in df.columns
            and not pd.isna(row["wbs_id"])
            else None
        )

        duration_days = (
            _clean_int(row["duration_days"])
            if "duration_days" in df.columns
            and not pd.isna(row["duration_days"])
            else None
        )

        progress_percent = (
            _clean_float(row["progress_percent"])
            if "progress_percent" in df.columns
            else 0
        )

        status = (
            _clean_string(row["status"])
            if "status" in df.columns
            and not pd.isna(row["status"])
            else "Not Started"
        )

        start_date = (
            _clean_date(row["start_date"])
            if "start_date" in df.columns
            and not pd.isna(row["start_date"])
            else None
        )

        finish_date = (
            _clean_date(row["finish_date"])
            if "finish_date" in df.columns
            and not pd.isna(row["finish_date"])
            else None
        )

        responsible_party = (
            _clean_string(row["responsible_party"])
            if "responsible_party" in df.columns
            and not pd.isna(row["responsible_party"])
            else None
        )

        # ------------------------------------------------
        # IDEMPOTENCY CHECK
        # Existing activity is identified by:
        # project_id + activity_code
        # ------------------------------------------------

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
                wbs_id=wbs_id,
                duration_days=duration_days,
                progress_percent=progress_percent,
                status=status,
                start_date=start_date,
                finish_date=finish_date,
                responsible_party=responsible_party,
            )

            db.add(activity)

            imported.append(activity)
            created_count += 1

        else:

            activity.activity_name = activity_name
            activity.wbs_id = wbs_id
            activity.duration_days = duration_days
            activity.progress_percent = progress_percent
            activity.status = status
            activity.start_date = start_date
            activity.finish_date = finish_date
            activity.responsible_party = responsible_party

            imported.append(activity)
            updated_count += 1

    db.commit()

    return {
        "project_id": project_id,
        "imported_count": len(imported),
        "created_count": created_count,
        "updated_count": updated_count,
        "status": "completed",
    }
