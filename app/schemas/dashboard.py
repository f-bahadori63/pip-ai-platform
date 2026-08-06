from typing import List, Optional
from pydantic import BaseModel


class ProgressKPI(BaseModel):

    planned_progress: float
    actual_progress: float
    variance: float



class ScheduleKPI(BaseModel):

    health: str
    delay_index: Optional[float] = None
    critical_activities: int



class AlertItem(BaseModel):

    level: str
    title: str
    message: str
    action: str



class RecoveryAction(BaseModel):

    required: bool
    priority: Optional[str] = None
    recommendation: Optional[str] = None



class DashboardResponse(BaseModel):

    project_id: int

    project_status: str

    progress: ProgressKPI

    schedule: ScheduleKPI

    alerts: List[AlertItem]

    recovery: RecoveryAction
