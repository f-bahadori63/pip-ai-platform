from pydantic import BaseModel
from typing import Optional


class WBSItemCreate(BaseModel):
    project_id: int
    parent_id: Optional[int] = None
    code: str
    name: str
    level: int = 1


class WBSItemRead(WBSItemCreate):
    id: int

    model_config = {
        "from_attributes": True
    }