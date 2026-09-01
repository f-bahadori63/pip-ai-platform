from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.base import Base


class ProjectCost(Base):

    __tablename__ = "project_costs"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )


    planned_cost = Column(
        Float,
        default=0
    )


    actual_cost = Column(
        Float,
        default=0
    )


    earned_value = Column(
        Float,
        default=0
    )


    # "manual"          -> entered by a user in the Cost page form
    # "schedule_import" -> auto-aggregated from cost columns detected
    #                       in an uploaded schedule Excel file
    source = Column(
        String(30),
        nullable=False,
        default="manual",
        server_default="manual",
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
