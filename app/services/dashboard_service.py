from app.schemas.dashboard import DashboardResponse


def build_dashboard_response(
    project_id: int,
    control_data: dict
):

    kpis = control_data.get(
        "kpis",
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


    schedule = control_data.get(
        "schedule",
        {}
    )


    schedule_items = schedule.get(
        "schedule_data",
        []
    )


    delay_indexes = [
        item.get("delay_index")
        for item in schedule_items
        if item.get("delay_index") is not None
    ]


    average_delay_index = None

    if delay_indexes:

        average_delay_index = round(
            sum(delay_indexes) / len(delay_indexes),
            3
        )


    return DashboardResponse(

        project_id=project_id,

        project_status=
            kpis.get(
                "schedule_health",
                "UNKNOWN"
            ),

        progress={

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

            "variance":
                kpis.get(
                    "schedule_variance",
                    0
                )

        },

        schedule={

            "health":
                kpis.get(
                    "schedule_health",
                    "UNKNOWN"
                ),

            "delay_index":
                average_delay_index,

            "critical_activities":
                kpis.get(
                    "critical_activities",
                    0
                )

        },

        alerts=alerts,

        recovery={

            "required":
                recovery.get(
                    "recovery_required",
                    False
                ),

            "priority":
                recovery.get(
                    "priority"
                ),

            "recommendation":
                recovery.get(
                    "recommendation"
                )

        }

    )