from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.schedule import (
    ScheduleActivityCreate,
    ScheduleActivityUpdate,
    ScheduleActivityResponse
)

from app.services.schedule_service import (
    create_activity,
    get_project_schedule,
    update_activity,
    delete_activity
)


router = APIRouter(
    prefix="/schedule",
    tags=["Schedule"]
)


@router.post(
    "/",
    response_model=ScheduleActivityResponse
)
def create_schedule_activity(
    data: ScheduleActivityCreate,
    db: Session = Depends(get_db)
):

    return create_activity(
        db,
        data
    )



@router.get(
    "/project/{project_id}",
    response_model=list[ScheduleActivityResponse]
)
def read_project_schedule(
    project_id: int,
    db: Session = Depends(get_db)
):

    return get_project_schedule(
        db,
        project_id
    )



@router.put(
    "/{activity_id}",
    response_model=ScheduleActivityResponse
)
def update_schedule_activity(
    activity_id:int,
    data:ScheduleActivityUpdate,
    db:Session=Depends(get_db)
):

    result = update_activity(
        db,
        activity_id,
        data
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return result



@router.delete(
    "/{activity_id}"
)
def remove_schedule_activity(
    activity_id:int,
    db:Session=Depends(get_db)
):

    result = delete_activity(
        db,
        activity_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return {
        "message":"Activity deleted"
    }