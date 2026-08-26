from datetime import datetime

from pydantic import BaseModel


class ScheduleActivityBase(BaseModel):

    activity_code: str
    activity_name: str

    wbs_id: int | None = None

    duration_days: int | None = None

    progress_percent: float | None = 0

    status: str | None = "Not Started"

    start_date: datetime | None = None

    finish_date: datetime | None = None

    responsible_party: str | None = None



class ScheduleActivityCreate(
    ScheduleActivityBase
):

    project_id: int



class ScheduleActivityUpdate(BaseModel):

    activity_name: str | None = None

    duration_days: int | None = None

    progress_percent: float | None = None

    status: str | None = None

    start_date: datetime | None = None

    finish_date: datetime | None = None

    responsible_party: str | None = None



class ScheduleActivityResponse(
    ScheduleActivityBase
):

    id: int

    project_id: int

    created_at: datetime


    class Config:
        from_attributes = True