from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.wbs import WBSItem
from app.schemas.wbs import WBSItemCreate, WBSItemRead
from app.services.wbs_import_service import clear_project_wbs

router = APIRouter(prefix="/wbs", tags=["WBS"])

@router.post("/", response_model=WBSItemRead)
def create_wbs_item(item: WBSItemCreate, db: Session = Depends(get_db)):
    db_item = WBSItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/project/{project_id}", response_model=list[WBSItemRead])
def get_project_wbs(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(WBSItem)
        .filter(WBSItem.project_id == project_id)
        .order_by(WBSItem.code)
        .all()
    )


@router.delete("/project/{project_id}")
def delete_project_wbs(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Remove stale WBS data for one project only."""

    try:
        deleted_count = clear_project_wbs(db, project_id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "project_id": project_id,
        "deleted_count": deleted_count,
        "status": "cleared",
    }
