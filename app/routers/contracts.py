from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


@router.post("/", response_model=ContractResponse)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db)
):
    db_contract = Contract(**contract.dict())

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


@router.get("/project/{project_id}", response_model=list[ContractResponse])
def get_project_contracts(
    project_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Contract)
        .filter(Contract.project_id == project_id)
        .all()
    )