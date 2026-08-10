from app.database.base import Base
from app.database.session import engine

from app.models import *

Base.metadata.create_all(
    bind=engine
)

print("DATABASE TABLES CREATED")
