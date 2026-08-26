from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    wbs_item_id = Column(Integer, ForeignKey("wbs_items.id"), nullable=True)

    risk_code = Column(String(50), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    category = Column(String(50), default="Technical")

    probability = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

    status = Column(String(50), default="Open")
    response_plan = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="risks")