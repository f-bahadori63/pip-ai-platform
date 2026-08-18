from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.project import Project

from app.services.ai.ollama_client import generate, MODEL_NAME
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
            "model": MODEL_NAME,
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
            "model": MODEL_NAME,
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
You are the Project Intelligence Assistant for PIP AI Platform.

You are answering a question about Project {project_id}.

IMPORTANT DATA RULES:
1. Use ONLY the PROJECT FACTS supplied below.
2. Never invent project values.
3. Never replace a supplied project status with your own interpretation.
4. Never confuse schedule health, risk level, recovery status, or project status.
5. If a requested value is not supplied, return N/A.
6. Preserve numeric values exactly as supplied.
7. Treat the structured PROJECT FACTS section as authoritative.
8. The user may ask for analysis, but factual KPI values must come from PROJECT FACTS.
9. For Project Status, use exactly the supplied Project Status value.
10. For Recovery Required:
    - If Recovery Required is TRUE, say that recovery is required.
    - If Recovery Required is FALSE, say that recovery is not required.
    - Do not substitute Recovery Status for Recovery Required.
11. Do not translate field names when the user explicitly requests exact field names.
12. Do not fabricate cost, schedule, risk, or activity information.

============================================================
PROJECT FACTS â€” AUTHORITATIVE
============================================================

Project ID: {project_id}
Project Status: {project.status}

SCHEDULE FACTS
Schedule Health: {kpis.get("schedule_health")}
Risk Level: {schedule.get("risk_level")}
Planned Progress: {kpis.get("planned_progress")}%
Actual Progress: {kpis.get("actual_progress")}%
Schedule Variance: {kpis.get("schedule_variance")}%
Critical Activities: {len(critical_activities)}
Recovery Status: {kpis.get("recovery_status")}

RECOVERY FACTS
Recovery Required: {kpis.get("recovery_status")}
Recovery Priority: {getattr(locals().get("recovery", None), "priority", None) if False else "See project recovery data"}
Recovery Recommendation:
{critical_text}

COST FACTS
Planned Cost: {costs.get("planned_cost")}
Actual Cost: {costs.get("actual_cost")}
Earned Value: {costs.get("earned_value")}
Remaining Cost: {costs.get("remaining_cost")}
Cost Variance: {costs.get("cost_variance")}
Cost Health: {costs.get("cost_health")}

CRITICAL ACTIVITIES
{critical_text}

============================================================
RESPONSE RULES
============================================================

For factual questions:
- Return the exact value from PROJECT FACTS.
- Do not infer a different value.

For analysis questions:
- First state the factual KPI values.
- Then provide a concise management interpretation.
- Clearly distinguish FACT from ANALYSIS.
- Do not change GREEN/RED/HIGH/MONITOR values.

User question:
{prompt}
"""

    response = generate(
        ai_prompt
    )

    return {
        "model": MODEL_NAME,
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
