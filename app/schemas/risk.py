from datetime import datetime

from pydantic import BaseModel


class RiskBase(BaseModel):
    risk_code: str
    title: str
    description: str | None = None
    category: str = "Technical"
    probability: int
    impact: int
    status: str = "Open"
    response_plan: str | None = None
    owner: str | None = None


class RiskCreate(RiskBase):
    project_id: int
    wbs_item_id: int | None = None


class RiskResponse(RiskBase):
    id: int
    project_id: int
    wbs_item_id: int | None
    score: int
    created_at: datetime

    class Config:
        from_attributes = True