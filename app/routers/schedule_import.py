from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.data_import.normalized_schedule_importer import normalize_and_import_schedule_excel

import os
import tempfile


router = APIRouter(
    prefix="/import",
    tags=["Import"]
)


@router.post("/schedule/{project_id}")
def import_schedule(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filename = file.filename or ""

    if not filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files are allowed"
        )

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

        result = normalize_and_import_schedule_excel(
            db=db,
            file_path=temp_path,
            project_id=project_id
        )

        return result

    finally:

        if temp_path and os.path.exists(temp_path):

            # ====================================================
            # SPRINT08F_WINDOWS_TEMP_CLEANUP
            #
            # Windows may keep the temporary Excel file locked
            # briefly after pandas/openpyxl processing.
            #
            # Cleanup must NEVER convert a successful import into
            # HTTP 500.
            # ====================================================

            cleanup_error = None

            for _cleanup_attempt in range(5):

                try:
                    os.remove(temp_path)
                    cleanup_error = None
                    break

                except PermissionError as exc:
                    cleanup_error = exc

                    import time
                    time.sleep(0.2)

            if cleanup_error is not None:

                # Do not raise cleanup errors into the HTTP layer.
                # The import operation itself has already completed.
                pass


