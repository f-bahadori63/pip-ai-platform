from sqlalchemy.orm import Session

from app.models.schedule import ScheduleActivity
from app.schemas.schedule import ScheduleActivityCreate, ScheduleActivityUpdate


def create_activity(
    db: Session,
    data: ScheduleActivityCreate
):

    activity = ScheduleActivity(
        **data.model_dump()
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity



def get_project_schedule(
    db: Session,
    project_id: int
):

    return (
        db.query(ScheduleActivity)
        .filter(
            ScheduleActivity.project_id == project_id
        )
        .all()
    )



def update_activity(
    db: Session,
    activity_id: int,
    data: ScheduleActivityUpdate
):

    activity = (
        db.query(ScheduleActivity)
        .filter(
            ScheduleActivity.id == activity_id
        )
        .first()
    )

    if not activity:
        return None


    for key,value in data.model_dump(
        exclude_unset=True
    ).items():

        setattr(activity,key,value)


    db.commit()
    db.refresh(activity)

    return activity



def delete_activity(
    db: Session,
    activity_id:int
):

    activity = (
        db.query(ScheduleActivity)
        .filter(
            ScheduleActivity.id == activity_id
        )
        .first()
    )

    if activity:
        db.delete(activity)
        db.commit()

    return activity