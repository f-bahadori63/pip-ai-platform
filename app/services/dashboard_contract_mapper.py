from app.schemas.dashboard_contract import ExecutiveDashboardContract


def map_dashboard_contract(
    dashboard_data: dict
):

    progress = dashboard_data.get(
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


    recommendation = recovery.get(
        "recommendation"
    )


    if not recommendation:
        recommendation = recovery.get("recommendation")


    return ExecutiveDashboardContract(

        project_id=dashboard_data.get(
            "project_id"
        ),

        health={

            "status": status,

            "title": "Project Health",

            "message":
                "Management attention required"
                if status == "RED"
                else "Project under control"

        },


        progress={

            "planned":
                progress.get(
                    "planned_progress",
                    0
                ),

            "actual":
                progress.get(
                    "actual_progress",
                    0
                ),

            "variance":
                progress.get(
                    "variance",
                    progress.get(
                        "schedule_variance",
                        0
                    )
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
                    recovery.get(
                        "recovery_required",
                        False
                    )
                ),

            "priority":
                recovery.get(
                    "priority"
                ),

            "action_plan":
                recommendation

        }

    )
