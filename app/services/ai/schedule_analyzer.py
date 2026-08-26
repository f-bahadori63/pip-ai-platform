from sqlalchemy.orm import Session

from app.models.schedule import ScheduleActivity
from app.services.schedule.critical_path_engine import calculate_critical_path
from app.services.schedule.metrics.delay_index import calculate_delay_index
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
            "schedule_data": [],
            "critical_path": {
                "critical_activities": [],
                "critical_count": 0,
                "method": "duration_based_cpm_v1",
            },
            "analysis": "No schedule activities found.",
            "recovery": {
                "recovery_required": False,
                "priority": "UNKNOWN",
                "recommendation": "No schedule data available.",
            },
        }

    critical_path = calculate_critical_path(
        activities
    )

    schedule_data = []

    for activity in activities:

        status_analysis = calculate_schedule_status(
            activity
        )

        planned_progress = status_analysis.get(
            "planned_progress",
            0
        )

        actual_progress = status_analysis.get(
            "actual_progress",
            0
        )

        delay_index = calculate_delay_index(
            {
                "planned_progress": planned_progress,
                "actual_progress": actual_progress,
            }
        )

        schedule_data.append(
            {
                "activity_name":
                    status_analysis.get(
                        "activity_name",
                        activity.activity_name,
                    ),

                "actual_progress":
                    actual_progress,

                "planned_progress":
                    planned_progress,

                "schedule_variance":
                    status_analysis.get(
                        "schedule_variance",
                        round(
                            actual_progress - planned_progress,
                            2
                        ),
                    ),

                "delay_index":
                    delay_index,

                "risk_level":
                    status_analysis.get(
                        "risk_level",
                        "UNKNOWN",
                    ),
            }
        )

    risk_levels = [
        item.get("risk_level")
        for item in schedule_data
    ]

    if "HIGH" in risk_levels:
        risk_level = "HIGH"

    elif "MEDIUM" in risk_levels:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    high_risk = [
        item
        for item in schedule_data
        if item.get("risk_level") == "HIGH"
    ]

    if high_risk:
        recovery_required = True
        priority = "HIGH"

        names = ", ".join(
            item["activity_name"]
            for item in high_risk[:3]
        )

        analysis = (
            f"Schedule risk is {risk_level}. "
            f"{len(high_risk)} high-risk activities require "
            f"management attention. Critical delayed activities: "
            f"{names}."
        )

    else:
        recovery_required = False
        priority = risk_level

        analysis = (
            f"Schedule risk is {risk_level}. "
            f"No high-risk schedule activity was detected "
            f"by the rule engine."
        )

    recovery = {
        "recovery_required": recovery_required,
        "priority": priority,
        "recommendation": (
            "Recovery workflow should be initiated for "
            "high-risk delayed activities."
            if recovery_required
            else
            "Continue schedule monitoring."
        ),
    }

    return {
        "project_id": project_id,
        "risk_level": risk_level,
        "activities_count": len(activities),
        "schedule_data": schedule_data,
        "critical_path": critical_path,
        "analysis": analysis,
        "recovery": recovery,
    }
