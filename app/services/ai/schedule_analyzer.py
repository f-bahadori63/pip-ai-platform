from sqlalchemy.orm import Session

from app.models.schedule import ScheduleActivity
from app.services.ai.ollama_client import generate
from app.services.schedule_control_engine import calculate_schedule_status


def analyze_project_schedule(
    db: Session,
    project_id: int
):

    activities = (
        db.query(ScheduleActivity)
        .filter(
            ScheduleActivity.project_id == project_id
        )
        .all()
    )

    if not activities:
        return {
            "project_id": project_id,
            "risk_level": "UNKNOWN",
            "activities_count": 0,
            "analysis": "No schedule activities found."
        }

    schedule_data = []

    for activity in activities:

        status_analysis = calculate_schedule_status(activity)

        schedule_data.append(status_analysis)

    risk_levels = [
        item.get("risk_level")
        for item in schedule_data
        if item.get("risk_level")
    ]

    if "HIGH" in risk_levels:
        risk_level = "HIGH"
    elif "MEDIUM" in risk_levels:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    prompt = f"""
You are a Senior EPC Project Controls Manager.

Analyze the following project schedule control data based on PMBOK principles.

Evaluate:
1. Current schedule status
2. Planned vs Actual progress
3. Schedule Variance
4. Delay risks
5. Critical activities
6. Recovery recommendations

Schedule Data:

{schedule_data}

Answer in Persian.
"""

    ai_response = generate(prompt)

    return {
        "project_id": project_id,
        "risk_level": risk_level,
        "activities_count": len(activities),
        "schedule_data": schedule_data,
        "analysis": ai_response
    }
