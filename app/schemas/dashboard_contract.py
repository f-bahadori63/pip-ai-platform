from typing import List, Optional
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

    delay_index: Optional[float]

    critical_items: int



class AlertCard(BaseModel):

    level: str

    title: str

    message: str

    action: str



class RecoveryCard(BaseModel):

    required: bool

    priority: Optional[str]

    action_plan: Optional[str]



class ExecutiveDashboardContract(BaseModel):

    project_id: int

    health: HealthCard

    progress: ProgressCard

    schedule: ScheduleCard

    alerts: List[AlertCard]

    recovery: RecoveryCard
