from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.base import Base


class Project(Base):

    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    code = Column(
        String,
        unique=True,
        index=True
    )

    description = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        default="Planning"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )