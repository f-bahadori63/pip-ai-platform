from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    project_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    client = Column(String(200), nullable=True)
    contract_value = Column(Float, nullable=True)
    currency = Column(String(20), default="IRR")
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="Planning")
    risks = relationship(
        "Risk",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wbs_items = relationship(
        "WBSItem",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    contracts = relationship(
        "Contract",
        back_populates="project",
        cascade="all, delete-orphan"
    )