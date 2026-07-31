from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://pip_user:pip_password@127.0.0.1:5432/pip_db"

engine = create_engine(
DATABASE_URL,
echo=True,
)

SessionLocal = sessionmaker(
autocommit=False,
autoflush=False,
bind=engine,
)

Base = declarative_base()
