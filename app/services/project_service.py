from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(
    db: Session,
    project: ProjectCreate
):
    db_project = Project(
        project_code=project.project_code,
        name=project.name,
        client=project.client,
        contract_value=project.contract_value,
        currency=project.currency,
        status=project.status
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


def get_projects(
    db: Session
):
    return db.query(Project).all()


def get_project(
    db: Session,
    project_id: int
):
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def update_project(
    db: Session,
    project_id: int,
    project: ProjectUpdate
):
    db_project = get_project(
        db,
        project_id
    )

    if not db_project:
        return None

    update_data = project.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_project,
            key,
            value
        )

    db.commit()
    db.refresh(db_project)

    return db_project


def delete_project(
    db: Session,
    project_id: int
):
    db_project = get_project(
        db,
        project_id
    )

    if not db_project:
        return None

    db.delete(db_project)
    db.commit()

    return db_project