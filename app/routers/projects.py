from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post(
    "/",
    response_model=ProjectResponse
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    return project_service.create_project(
        db,
        project
    )


@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def read_projects(
    db: Session = Depends(get_db)
):
    return project_service.get_projects(db)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def read_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    updated = project_service.update_project(
        db,
        project_id,
        project
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return updated


@router.delete(
    "/{project_id}"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    deleted = project_service.delete_project(
        db,
        project_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "message": "Project deleted successfully"
    }