from app.database.session import engine
from app.database.base import Base

from app.models import Project, WBSItem, Contract


def init_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
