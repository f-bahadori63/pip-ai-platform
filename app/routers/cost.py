from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.cost.cost import ProjectCost
from app.services.cost.cost_engine import calculate_cost_kpis


router = APIRouter(
    prefix="/cost",
    tags=["Cost"]
)


@router.post("/project/{project_id}")
def create_cost(
    project_id: int,
    planned_cost: float,
    actual_cost: float = 0,
    earned_value: float = 0,
    db: Session = Depends(get_db)
):

    cost = ProjectCost(

        project_id=project_id,

        planned_cost=planned_cost,

        actual_cost=actual_cost,

        earned_value=earned_value
    )


    db.add(cost)

    db.commit()

    db.refresh(cost)


    return {

        "id": cost.id,

        "project_id": project_id,

        "status": "created"

    }



@router.get("/project/{project_id}")
def get_cost(
    project_id: int,
    db: Session = Depends(get_db)
):

    return calculate_cost_kpis(
        db,
        project_id
    )