
from pydantic import BaseModel


class HealthCard(BaseModel):

    status: str

    title: str

    message: str



class ProgressCard(BaseModel):

    planned: float

    actual: float

    variance: float



class ScheduleCard(BaseModel):

    health: str

    delay_index: float | None

    critical_items: int



class AlertCard(BaseModel):

    level: str

    title: str

    message: str

    action: str



class RecoveryCard(BaseModel):

    required: bool

    priority: str | None

    action_plan: str | None



class ExecutiveDashboardContract(BaseModel):

    project_id: int

    health: HealthCard

    progress: ProgressCard

    schedule: ScheduleCard

    alerts: list[AlertCard]

    recovery: RecoveryCard
