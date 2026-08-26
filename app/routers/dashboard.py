from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.ai.project_control_center import build_project_control_center
from app.services.ai.project_summary import generate_project_summary
from app.services.dashboard_service import build_dashboard_response

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/project/{project_id}")
def project_dashboard(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )

    dashboard = build_dashboard_response(
        project_id,
        control_data
    )

    return dashboard



@router.get("/ai-summary/{project_id}")
def ai_project_summary(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )

    dashboard_data = build_dashboard_response(
        project_id,
        control_data
    )

    summary = generate_project_summary(
        dashboard_data
    )

    return {
        "project_id": project_id,
        "summary": summary
    }



@router.get("/executive/{project_id}")
def executive_dashboard(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )

    return build_dashboard_response(
        project_id,
        control_data
    )



@router.get("/critical-activities/{project_id}")
def critical_activities_dashboard(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )

    schedule = control_data.get(
        "schedule",
        {}
    )

    activities = schedule.get(
        "schedule_data",
        []
    )

    critical = [
        item for item in activities
        if item.get("risk_level") == "HIGH"
    ]

    return {
        "project_id": project_id,
        "count": len(critical),
        "activities": critical
    }
