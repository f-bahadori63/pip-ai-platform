from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.schemas.risk import RiskCreate


def calculate_score(probability: int, impact: int) -> int:
    return probability * impact


def create_risk(db: Session, risk_data: RiskCreate):
    risk = Risk(
        **risk_data.model_dump(),
        score=calculate_score(risk_data.probability, risk_data.impact)
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


def get_project_risks(db: Session, project_id: int):
    return (
        db.query(Risk)
        .filter(Risk.project_id == project_id)
        .order_by(Risk.score.desc())
        .all()
    )


def get_risk_heatmap(db: Session, project_id: int):
    risks = get_project_risks(db, project_id)

    return [
        {
            "risk_code": r.risk_code,
            "title": r.title,
            "probability": r.probability,
            "impact": r.impact,
            "score": r.score,
            "level": (
                "Critical" if r.score >= 16
                else "High" if r.score >= 11
                else "Medium" if r.score >= 6
                else "Low"
            )
        }
        for r in risks
    ]