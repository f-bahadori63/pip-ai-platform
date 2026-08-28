from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.analysis_service import run_project_analysis

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post("/project/{project_id}/run")
def run_management_analysis(
    project_id: int,
    db: Session = Depends(get_db)
):

    try:

        return run_project_analysis(
            db,
            project_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
