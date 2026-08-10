from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.project import Project

from app.services.ai.ollama_client import generate
from app.services.ai.project_assistant import build_project_summary

from app.services.ai.schedule_analyzer import analyze_project_schedule
from app.services.ai.schedule_recovery import generate_recovery_plan

from app.services.project_control_kpi import calculate_project_kpis
from app.services.project_alert_engine import generate_project_alerts

from app.services.ai.executive_report import generate_executive_report
from app.services.ai.project_control_center import (
    build_project_control_center
)

from app.services.cost.cost_engine import calculate_cost_kpis


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/chat")
def local_chat(
    prompt: str = Query(...),
    project_id: int | None = Query(None),
    db: Session = Depends(get_db),
):

    if project_id is None:

        response = generate(
            prompt
        )

        return {
            "model": "qwen2.5:3b",
            "response": response,
            "done": True,
            "project_id": None,
        }

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id
        )
        .first()
    )

    if not project:

        return {
            "model": "qwen2.5:3b",
            "response": "Project not found.",
            "done": True,
            "project_id": project_id,
        }

    schedule = analyze_project_schedule(
        db,
        project_id
    )

    kpis = calculate_project_kpis(
        schedule
    )

    costs = calculate_cost_kpis(
        db,
        project_id
    )

    alerts = generate_project_alerts(
        kpis
    )

    critical_activities = [
        item
        for item in schedule.get(
            "schedule_data",
            []
        )
        if item.get("risk_level") == "HIGH"
    ][:3]

    critical_text = "\n".join(
        (
            f"- {item['activity_name']}: "
            f"Actual={item['actual_progress']}%, "
            f"Planned={item['planned_progress']}%, "
            f"Variance={item['schedule_variance']}%, "
            f"DelayIndex={item['delay_index']}"
        )
        for item in critical_activities
    )

    if not critical_text:
        critical_text = "No high-risk activities."

    alert_text = "\n".join(
        (
            f"- {item.get('level')}: "
            f"{item.get('title')}"
        )
        for item in alerts
    )

    if not alert_text:
        alert_text = "No active alerts."

    context = f"""
PIP PROJECT CONTEXT

Project Code: {project.project_code}
Project Name: {project.name}
Client: {project.client}
Project Status: {project.status}

SCHEDULE
Schedule Health: {kpis.get("schedule_health")}
Risk Level: {schedule.get("risk_level")}
Planned Progress: {kpis.get("planned_progress")}%
Actual Progress: {kpis.get("actual_progress")}%
Schedule Variance: {kpis.get("schedule_variance")}%
Critical Activities: {len(critical_activities)}
Recovery Required: {kpis.get("recovery_status")}

CRITICAL ACTIVITIES
{critical_text}

COST
Planned Cost: {costs.get("planned_cost")}
Actual Cost: {costs.get("actual_cost")}
Earned Value: {costs.get("earned_value")}
Remaining Cost: {costs.get("remaining_cost")}
Cost Variance: {costs.get("cost_variance")}
Cost Health: {costs.get("cost_health")}

ALERTS
{alert_text}
"""

    ai_prompt = f"""
You are PIP Project Intelligence Assistant.

You are an expert EPC project controls manager
for Oil & Gas, Petrochemical, Steel and Industrial EPC projects.

Use ONLY the project data supplied below.
Do not invent missing information.

PROJECT DATA:
{context}

USER QUESTION:
{prompt}

Answer in professional Persian.

Rules:
- Maximum 5 short sentences.
- Use actual project numbers.
- Clearly distinguish facts from recommendations.
- If schedule recovery is required, say so explicitly.
- Do not say that you lack project data.
"""

    response = generate(
        ai_prompt
    )

    return {
        "model": "qwen2.5:3b",
        "response": response,
        "done": True,
        "project_id": project_id,
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
def project_summary(
    project_id: int,
    db: Session = Depends(get_db)
):

    return build_project_summary(
        db,
        project_id
    )


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
            schedule_result.get(
                "schedule_data",
                []
            )
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
