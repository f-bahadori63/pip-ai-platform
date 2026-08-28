"""Regression tests for upload-driven WBS replacement."""

from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Register every relationship target before configuring the in-memory schema.
from app.database.base import Base
from app.models import Project, Risk, ScheduleActivity, WBSItem  # noqa: F401
from app.services.data_import.normalization_models import NormalizationResult
from app.services.data_import.schedule_importer import import_schedule_excel
from app.services.data_import.schedule_normalizer import normalize_schedule_excel
from app.services.wbs_import_service import replace_project_wbs_from_schedule


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def _project(db, code: str = "P-001") -> Project:
    project = Project(project_code=code, name="Test Project")
    db.add(project)
    db.flush()
    return project


def test_replace_removes_old_wbs_and_builds_uploaded_hierarchy(db):
    project = _project(db)
    old_root = WBSItem(
        project_id=project.id,
        code="1",
        name="Old WBS",
        level=1,
    )
    db.add(old_root)
    db.flush()

    old_child = WBSItem(
        project_id=project.id,
        parent_id=old_root.id,
        code="1.1",
        name="Old Child",
        level=2,
    )
    db.add(old_child)
    db.flush()

    first = ScheduleActivity(
        project_id=project.id,
        wbs_id=old_child.id,
        activity_code="NEW-001",
        activity_name="Site Survey",
    )
    second = ScheduleActivity(
        project_id=project.id,
        wbs_id=old_child.id,
        activity_code="NEW-002",
        activity_name="Detailed Design",
    )
    risk = Risk(
        project_id=project.id,
        wbs_item_id=old_child.id,
        risk_code="R-WBS-1",
        title="Old link",
        probability=1,
        impact=1,
        score=1,
    )
    db.add_all([first, second, risk])
    db.flush()

    result = replace_project_wbs_from_schedule(
        db,
        project.id,
        [
            {
                "activity_code": "NEW-001",
                "activity_name": "Site Survey",
                "wbs_code": "2.1",
                "wbs_name": "Survey Package",
            },
            {
                "activity_code": "NEW-002",
                "activity_name": "Detailed Design",
                "wbs_code": "2.2",
                "wbs_name": "Design Package",
            },
        ],
    )
    db.commit()

    items = db.query(WBSItem).filter_by(project_id=project.id).all()
    by_code = {item.code: item for item in items}

    assert result == {
        "source": "latest_upload",
        "replaced_count": 2,
        "created_count": 3,
        "linked_activities": 2,
        "total_items": 3,
    }
    assert set(by_code) == {"2", "2.1", "2.2"}
    assert by_code["2.1"].name == "Survey Package"
    assert by_code["2.1"].parent_id == by_code["2"].id
    assert by_code["2.2"].parent_id == by_code["2"].id
    assert first.wbs_id == by_code["2.1"].id
    assert second.wbs_id == by_code["2.2"].id
    assert risk.wbs_item_id is None


def test_replace_derives_wbs_when_file_has_no_wbs_column(db):
    project = _project(db)
    activities = [
        ScheduleActivity(
            project_id=project.id,
            activity_code="ENG-001",
            activity_name="Survey",
        ),
        ScheduleActivity(
            project_id=project.id,
            activity_code="ENG-002",
            activity_name="Design",
        ),
    ]
    db.add_all(activities)
    db.flush()

    result = replace_project_wbs_from_schedule(
        db,
        project.id,
        [
            {"activity_code": "ENG-001", "activity_name": "Survey"},
            {"activity_code": "ENG-002", "activity_name": "Design"},
        ],
    )
    db.commit()

    item = db.query(WBSItem).filter_by(project_id=project.id).one()

    assert item.code == "ENG"
    assert item.name == "ENG"
    assert result["linked_activities"] == 2
    assert {activity.wbs_id for activity in activities} == {item.id}


def test_zero_suffix_root_is_preserved_and_used_as_parent(db):
    project = _project(db)
    activities = [
        ScheduleActivity(
            project_id=project.id,
            activity_code="A010",
            activity_name="Project Management",
        ),
        ScheduleActivity(
            project_id=project.id,
            activity_code="A011",
            activity_name="Kick-off Meeting",
        ),
    ]
    db.add_all(activities)
    db.flush()

    replace_project_wbs_from_schedule(
        db,
        project.id,
        [
            {
                "activity_code": "A010",
                "activity_name": "Project Management",
                "wbs_code": "2.0",
            },
            {
                "activity_code": "A011",
                "activity_name": "Kick-off Meeting",
                "wbs_code": "2.1",
            },
        ],
    )
    db.commit()

    items = db.query(WBSItem).filter_by(project_id=project.id).all()
    by_code = {item.code: item for item in items}

    assert set(by_code) == {"2.0", "2.1"}
    assert by_code["2.0"].level == 1
    assert by_code["2.1"].level == 2
    assert by_code["2.1"].parent_id == by_code["2.0"].id


def test_normalizer_preserves_wbs_code_and_name(tmp_path):
    path = tmp_path / "schedule.xlsx"
    pd.DataFrame(
        [
            {
                "Activity Code": "A-001",
                "Activity Name": "Foundation",
                "WBS Code": "3.1.2",
                "WBS Name": "Civil Works",
            }
        ]
    ).to_excel(path, index=False)

    result = normalize_schedule_excel(path)

    assert result.status == "ready"
    assert result.normalized_rows[0]["wbs_code"] == "3.1.2"
    assert result.normalized_rows[0]["wbs_name"] == "Civil Works"


def test_failed_normalization_does_not_delete_existing_wbs(db, monkeypatch):
    project = _project(db)
    existing = WBSItem(
        project_id=project.id,
        code="OLD",
        name="Keep until upload is valid",
        level=1,
    )
    db.add(existing)
    db.commit()

    monkeypatch.setattr(
        "app.services.data_import.schedule_importer.normalize_schedule_excel",
        lambda _path: NormalizationResult(status="needs_user_input"),
    )

    result = import_schedule_excel(db, "ignored.xlsx", project.id)

    assert result["imported"] is False
    assert db.query(WBSItem).filter_by(project_id=project.id).count() == 1
