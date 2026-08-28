
from pydantic import BaseModel


class ProgressKPI(BaseModel):

    planned_progress: float
    actual_progress: float
    variance: float



class ScheduleKPI(BaseModel):

    health: str
    delay_index: float | None = None
    critical_activities: int



class CostKPI(BaseModel):

    planned_cost: float = 0
    actual_cost: float = 0
    earned_value: float = 0
    remaining_cost: float = 0
    cost_variance: float = 0
    cost_health: str = "UNKNOWN"
    evm: dict | None = None



class AlertItem(BaseModel):

    level: str
    title: str
    message: str
    action: str



class RecoveryAction(BaseModel):

    required: bool
    priority: str | None = None
    recommendation: str | None = None



class DashboardResponse(BaseModel):

    project_id: int

    project_status: str

    progress: ProgressKPI

    schedule: ScheduleKPI

    cost: CostKPI

    alerts: list[AlertItem]

    recovery: RecoveryAction