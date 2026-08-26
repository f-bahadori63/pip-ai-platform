from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    project_code: str
    name: str
    client: str | None = None
    contract_value: float | None = None
    currency: str | None = "IRR"
    status: str | None = "Planning"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_code: str | None = None
    name: str | None = None
    client: str | None = None
    contract_value: float | None = None
    currency: str | None = None
    status: str | None = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True