from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.risk_register.risk_register import ProjectRisk

router = APIRouter(
    prefix="/risk",
    tags=["Risk Register"]
)


@router.post("/project/{project_id}")
def create_risk(
    project_id: int,
    risk_code: str,
    risk_title: str,
    category: str,
    probability: float,
    impact: float,
    response_action: str,
    db: Session = Depends(get_db)
):

    risk_score = probability * impact


    risk = ProjectRisk(

        project_id=project_id,

        risk_code=risk_code,

        risk_title=risk_title,

        category=category,

        probability=probability,

        impact=impact,

        risk_score=risk_score,

        response_action=response_action

    )


    db.add(risk)
    db.commit()
    db.refresh(risk)


    return {

        "id": risk.id,

        "project_id": project_id,

        "risk_score": risk_score,

        "status": "created"

    }



@router.get("/project/{project_id}")
def get_risks(
    project_id: int,
    db: Session = Depends(get_db)
):

    risks = (

        db.query(ProjectRisk)

        .filter(
            ProjectRisk.project_id == project_id
        )

        .all()

    )


    return {

        "project_id": project_id,

        "count": len(risks),

        "risks": [

            {

                "id": r.id,

                "code": r.risk_code,

                "title": r.risk_title,

                "category": r.category,

                "probability": r.probability,

                "impact": r.impact,

                "risk_score": r.risk_score,

                "action": r.response_action,

                "status": r.status

            }

            for r in risks

        ]

    }