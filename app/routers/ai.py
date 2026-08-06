from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.services.ai.schedule_analyzer import analyze_project_schedule
from app.services.ai.schedule_recovery import generate_recovery_plan
from app.services.project_control_kpi import calculate_project_kpis
from app.services.project_alert_engine import generate_project_alerts
from app.services.ai.executive_report import generate_executive_report
from app.services.ai.project_control_center import build_project_control_center
from app.database.connection import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.session import get_db
from app.services.ai.ollama_client import generate
from app.services.ai.project_assistant import build_project_summary

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
def local_chat(prompt: str = Query(...)):
    response = generate(prompt)

    return {
        "model": "qwen2.5:3b",
        "response": response,
        "done": True,
    }

@router.get("/schedule-analysis/{project_id}")
def schedule_analysis(
    project_id: int,
    db: Session = Depends(get_db)
):

    return analyze_project_schedule(
        db,
        project_id
    )
@router.get("/project-summary/{project_id}")
def project_summary(project_id: int, db: Session = Depends(get_db)):
    return build_project_summary(db, project_id)

@router.get("/schedule-recovery/{project_id}")
def schedule_recovery(
    project_id: int,
    db: Session = Depends(get_db)
):

    schedule_result = analyze_project_schedule(
        db,
        project_id
    )

    return {
        "project_id": project_id,
        **generate_recovery_plan(
            schedule_result["schedule_data"]
        )
    }

@router.get("/project-kpi/{project_id}")
def project_kpi(
    project_id: int,
    db: Session = Depends(get_db)
):

    schedule_analysis = analyze_project_schedule(
        db,
        project_id
    )

    return {
        "project_id": project_id,
        "kpis": calculate_project_kpis(
            schedule_analysis
        )
    }


@router.get("/project-alerts/{project_id}")
def project_alerts(
    project_id: int,
    db: Session = Depends(get_db)
):

    schedule_analysis = analyze_project_schedule(
        db,
        project_id
    )


    kpis = calculate_project_kpis(
        schedule_analysis
    )


    return {
        "project_id": project_id,
        "alerts": generate_project_alerts(
            kpis
        )
    }


@router.get("/project-status-report/{project_id}")
def project_status_report(
    project_id: int,
    db: Session = Depends(get_db)
):

    schedule_analysis = analyze_project_schedule(
        db,
        project_id
    )


    kpis = calculate_project_kpis(
        schedule_analysis
    )


    alerts = generate_project_alerts(
        kpis
    )


    report = generate_executive_report(
        schedule_analysis,
        kpis,
        alerts
    )


    return {
        "project_id": project_id,
        **report
    }


@router.get("/project-control-center/{project_id}")
def project_control_center(
    project_id: int,
    db: Session = Depends(get_db)
):

    return build_project_control_center(
        db,
        project_id
    )

