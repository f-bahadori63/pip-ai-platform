from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    contract_number = Column(String, nullable=True)

    contractor = Column(String, nullable=True)

    client = Column(String, nullable=True)

    contract_value = Column(Float, nullable=True)

    currency = Column(
        String,
        default="IRR"
    )

    start_date = Column(Date, nullable=True)

    end_date = Column(Date, nullable=True)

    contract_type = Column(
        String,
        default="EPC"
    )

    description = Column(String, nullable=True)


    project = relationship(
        "Project",
        back_populates="contracts"
    )