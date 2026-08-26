
from pydantic import BaseModel


class WBSItemCreate(BaseModel):
    project_id: int
    parent_id: int | None = None
    code: str
    name: str
    level: int = 1


class WBSItemRead(WBSItemCreate):
    id: int

    model_config = {
        "from_attributes": True
    }