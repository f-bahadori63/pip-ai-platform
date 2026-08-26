from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class WBSItem(Base):
    __tablename__ = "wbs_items"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("wbs_items.id"), nullable=True)

    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)

    project = relationship("Project", back_populates="wbs_items")

    children = relationship(
        "WBSItem",
        backref="parent",
        remote_side=[id]
    )