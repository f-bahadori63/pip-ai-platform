from datetime import date, datetime

from pydantic import BaseModel


class ContractBase(BaseModel):
    contract_number: str | None = None
    contractor: str | None = None
    client: str | None = None
    contract_value: float | None = None
    currency: str = "IRR"
    start_date: date | None = None
    end_date: date | None = None
    contract_type: str = "EPC"
    description: str | None = None


class ContractCreate(ContractBase):
    project_id: int


class ContractResponse(ContractBase):
    id: int
    project_id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True