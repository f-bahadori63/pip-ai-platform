from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.ai.project_control_center import build_project_control_center

router = APIRouter(
    prefix="/demo",
    tags=["Demo"]
)


@router.get("/project/{project_id}")
def demo_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )


    kpis = control_data.get(
        "kpis",
        {}
    )


    schedule = control_data.get(
        "schedule",
        {}
    )


    alerts = control_data.get(
        "alerts",
        []
    )


    recovery = control_data.get(
        "recovery",
        {}
    )


    critical_path = schedule.get(
        "critical_path",
        {}
    )


    critical_activities = critical_path.get(
        "critical_activities",
        []
    )


    costs = control_data.get(
        "costs",
        {}
    )


    return {

        "project_id": project_id,


        "project_status":
            kpis.get(
                "schedule_health",
                "UNKNOWN"
            ),


        "kpi": {

            "planned_progress":
                kpis.get(
                    "planned_progress",
                    0
                ),


            "actual_progress":
                kpis.get(
                    "actual_progress",
                    0
                ),


            "schedule_variance":
                kpis.get(
                    "schedule_variance",
                    0
                ),


            "cost_health":
                costs.get(
                    "cost_health",
                    "UNKNOWN"
                )

        },


        "schedule": {

            "delay_index":
                kpis.get(
                    "schedule_variance",
                    0
                ),


            "critical_activities":
                len(
                    critical_activities
                )

        },


        "alerts": alerts,


        "insight": {

            "required":
                recovery.get(
                    "recovery_required",
                    False
                ),


            "priority":
                recovery.get(
                    "priority"
                ),


            "critical_activities":
                recovery.get(
                    "critical_activities",
                    []
                ),


            "recommendation":
                recovery.get(
                    "recommendation",
                    "No AI recommendation available."
                )

        }

    }