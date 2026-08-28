"""Tests for filename-based project resolution."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models import Project  # noqa: F401
from app.services.project_file_resolver import (
    project_name_from_filename,
    resolve_project_from_filename,
)


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_project_name_is_cleaned_from_filename():
    assert (
        project_name_from_filename(r"C:\fake\Tank_Project-Schedule.xlsx")
        == "Tank Project Schedule"
    )


def test_resolver_creates_project_from_filename():
    db = _session()

    try:
        project, created = resolve_project_from_filename(
            db,
            "Tank_Project-Schedule.xlsx",
        )
        db.commit()

        assert created is True
        assert project.name == "Tank Project Schedule"
        assert project.project_code == "TANK-PROJECT-SCHEDULE"
    finally:
        db.close()


def test_resolver_reuses_case_insensitive_name_match():
    db = _session()

    try:
        existing = Project(
            project_code="TANK-001",
            name="Tank Project Schedule",
        )
        db.add(existing)
        db.commit()

        project, created = resolve_project_from_filename(
            db,
            "tank_project_schedule.xlsx",
        )

        assert created is False
        assert project.id == existing.id
        assert db.query(Project).count() == 1
    finally:
        db.close()


def test_resolver_generates_unique_project_code():
    db = _session()

    try:
        db.add(Project(project_code="PROJECT", name="Different"))
        db.commit()

        project, created = resolve_project_from_filename(db, "پروژه.xlsx")

        assert created is True
        assert project.project_code == "PROJECT-2"
    finally:
        db.close()
