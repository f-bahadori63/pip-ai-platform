import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.data_import.schedule_importer import import_schedule_excel

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

        result = import_schedule_excel(
            db=db,
            file_path=temp_path,
            project_id=project_id
        )

        return result

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
