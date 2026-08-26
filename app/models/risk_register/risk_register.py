from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.base import Base


class ProjectRisk(Base):

    __tablename__ = "project_risks"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    risk_code = Column(
        String(50),
        nullable=False
    )

    risk_title = Column(
        String(200),
        nullable=False
    )

    category = Column(
        String(100)
    )

    probability = Column(
        Float,
        default=0
    )

    impact = Column(
        Float,
        default=0
    )

    risk_score = Column(
        Float,
        default=0
    )

    response_action = Column(
        String(500)
    )

    status = Column(
        String(50),
        default="Open"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )