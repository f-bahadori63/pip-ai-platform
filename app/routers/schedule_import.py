import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.data_import.schedule_importer import import_schedule_excel
from app.services.project_file_resolver import (
    project_resolution_payload,
    resolve_project_from_filename,
)

router = APIRouter(
    prefix="/import",
    tags=["Import"]
)


def _import_schedule_file(
    file: UploadFile,
    db: Session,
    requested_project_id: int | None = None,
):
    filename = file.filename or ""

    if not filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files are allowed"
        )

    try:
        project, project_created = resolve_project_from_filename(
            db,
            filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project_payload = project_resolution_payload(project, project_created)
    suffix = os.path.splitext(filename)[1].lower()
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        result = import_schedule_excel(
            db=db,
            file_path=temp_path,
            project_id=project.id,
        )

        if not result.get("imported", False) and project_created:
            # Do not leave an empty project behind when normalization rejects
            # the uploaded workbook.
            db.rollback()

        return {
            **result,
            "project_id": project_payload["id"],
            "project": project_payload,
            "requested_project_id": requested_project_id,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/schedule")
def import_schedule_by_filename(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Find or create the upload target project from the filename."""

    return _import_schedule_file(file=file, db=db)


@router.post("/schedule/{project_id}")
def import_schedule(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Backward-compatible route; filename resolution remains authoritative."""

    return _import_schedule_file(
        file=file,
        db=db,
        requested_project_id=project_id,
    )
