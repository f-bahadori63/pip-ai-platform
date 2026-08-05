from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ContractBase(BaseModel):
    contract_number: Optional[str] = None
    contractor: Optional[str] = None
    client: Optional[str] = None
    contract_value: Optional[float] = None
    currency: str = "IRR"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_type: str = "EPC"
    description: Optional[str] = None


class ContractCreate(ContractBase):
    project_id: int


class ContractResponse(ContractBase):
    id: int
    project_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True