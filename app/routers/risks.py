
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.risk import RiskCreate, RiskResponse
from app.services.risk_service import (
    create_risk,
    get_project_risks,
    get_risk_heatmap,
)

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.post("/", response_model=RiskResponse)
def create_new_risk(risk: RiskCreate, db: Session = Depends(get_db)):
    return create_risk(db, risk)


@router.get("/project/{project_id}", response_model=list[RiskResponse])
def get_risks(project_id: int, db: Session = Depends(get_db)):
    return get_project_risks(db, project_id)


@router.get("/project/{project_id}/heatmap")
def get_heatmap(project_id: int, db: Session = Depends(get_db)):
    return get_risk_heatmap(db, project_id)