from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RiskBase(BaseModel):
    risk_code: str
    title: str
    description: Optional[str] = None
    category: str = "Technical"
    probability: int
    impact: int
    status: str = "Open"
    response_plan: Optional[str] = None
    owner: Optional[str] = None


class RiskCreate(RiskBase):
    project_id: int
    wbs_item_id: Optional[int] = None


class RiskResponse(RiskBase):
    id: int
    project_id: int
    wbs_item_id: Optional[int]
    score: int
    created_at: datetime

    class Config:
        from_attributes = True