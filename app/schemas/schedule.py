from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScheduleActivityBase(BaseModel):

    activity_code: str
    activity_name: str

    wbs_id: Optional[int] = None

    duration_days: Optional[int] = None

    progress_percent: Optional[float] = 0

    status: Optional[str] = "Not Started"

    start_date: Optional[datetime] = None

    finish_date: Optional[datetime] = None

    responsible_party: Optional[str] = None



class ScheduleActivityCreate(
    ScheduleActivityBase
):

    project_id: int



class ScheduleActivityUpdate(BaseModel):

    activity_name: Optional[str] = None

    duration_days: Optional[int] = None

    progress_percent: Optional[float] = None

    status: Optional[str] = None

    start_date: Optional[datetime] = None

    finish_date: Optional[datetime] = None

    responsible_party: Optional[str] = None



class ScheduleActivityResponse(
    ScheduleActivityBase
):

    id: int

    project_id: int

    created_at: datetime


    class Config:
        from_attributes = True