from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    project_code: str
    name: str
    client: Optional[str] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = "IRR"
    status: Optional[str] = "Planning"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_code: Optional[str] = None
    name: Optional[str] = None
    client: Optional[str] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True