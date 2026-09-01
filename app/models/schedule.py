from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class ScheduleActivity(Base):

    __tablename__ = "schedule_activities"

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

    wbs_id = Column(
        Integer,
        ForeignKey("wbs_items.id"),
        nullable=True
    )

    activity_code = Column(
        String(50),
        nullable=False
    )

    activity_name = Column(
        String(200),
        nullable=False
    )

    duration_days = Column(
        Integer,
        nullable=True
    )

    progress_percent = Column(
        Float,
        default=0
    )

    status = Column(
        String(50),
        default="Not Started"
    )

    start_date = Column(
        DateTime,
        nullable=True
    )

    finish_date = Column(
        DateTime,
        nullable=True
    )

    responsible_party = Column(
        String(200),
        nullable=True
    )

    # Optional cost-loaded-schedule fields. Populated automatically when
    # the uploaded Excel workbook contains matching financial columns
    # (e.g. "Budgeted Cost" / BCWS, "Actual Cost" / ACWP, "Earned Value" /
    # BCWP). Left NULL when the schedule has no financial data.
    budgeted_cost = Column(
        Float,
        nullable=True
    )

    actual_cost = Column(
        Float,
        nullable=True
    )

    earned_value = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    project = relationship(
        "Project",
        back_populates="schedule_activities"
    )
