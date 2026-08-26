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

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    project = relationship(
        "Project",
        back_populates="schedule_activities"
    )
