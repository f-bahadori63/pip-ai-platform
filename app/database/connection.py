"""
Legacy compatibility layer.

The canonical database implementation lives in app.database.session.
This module intentionally does NOT create a second Engine, SessionLocal,
or SQLAlchemy Base.

Existing legacy imports can continue to work while the application
gradually converges on the canonical database layer.
"""

from app.database.base import Base
from app.database.session import engine, SessionLocal, get_db

DATABASE_URL = str(engine.url)
