from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.wbs import WBSItem
from app.models.schedule import ScheduleActivity
from app.schemas.wbs import WBSItemCreate, WBSItemRead

router = APIRouter(prefix="/wbs", tags=["WBS"])

@router.post("/", response_model=WBSItemRead)
def create_wbs_item(item: WBSItemCreate, db: Session = Depends(get_db)):
    db_item = WBSItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/project/{project_id}", response_model=list[WBSItemRead])
@router.get("/project/{project_id}", response_model=list[WBSItemRead])

def get_project_wbs(project_id: int, db: Session = Depends(get_db)):
    current_wbs_ids = (
        db.query(ScheduleActivity.wbs_id)
        .filter(
            ScheduleActivity.project_id == project_id,
            ScheduleActivity.wbs_id.isnot(None),
        )
        .distinct()
        .subquery()
    )

    return (
        db.query(WBSItem)
        .filter(
            WBSItem.project_id == project_id,
            WBSItem.id.in_(current_wbs_ids),
        )
        .order_by(WBSItem.level, WBSItem.code, WBSItem.id)
        .all()
    )

