from app.database.connection import engine
from app.database.base import Base

from app.models.project import Project


def init_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()