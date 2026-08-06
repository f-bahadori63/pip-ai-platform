from app.schemas.dashboard_contract import (
    ExecutiveDashboardContract
)


def map_dashboard_contract(
    dashboard_data: dict
):

    kpis = dashboard_data.get(
        "progress",
        {}
    )


    schedule = dashboard_data.get(
        "schedule",
        {}
    )


    alerts = dashboard_data.get(
        "alerts",
        []
    )


    recovery = dashboard_data.get(
        "recovery",
        {}
    )


    status = dashboard_data.get(
        "project_status",
        "UNKNOWN"
    )


    return ExecutiveDashboardContract(

        project_id=
            dashboard_data.get(
                "project_id"
            ),

        health={

            "status": status,

            "title":
                "Project Health",

            "message":
                "Management attention required"
                if status == "RED"
                else "Project under control"

        },

        progress={

            "planned":
                kpis.get(
                    "planned_progress",
                    0
                ),

            "actual":
                kpis.get(
                    "actual_progress",
                    0
                ),

            "variance":
                kpis.get(
                    "variance",
                    0
                )

        },

        schedule={

            "health":
                schedule.get(
                    "health"
                ),

            "delay_index":
                schedule.get(
                    "delay_index"
                ),

            "critical_items":
                schedule.get(
                    "critical_activities",
                    0
                )

        },

        alerts=alerts,

        recovery={

            "required":
                recovery.get(
                    "required",
                    False
                ),

            "priority":
                recovery.get(
                    "priority"
                ),

            "action_plan":
                recovery.get(
                    "recommendation"
                )

        }

    )
