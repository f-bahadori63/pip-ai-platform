def calculate_project_kpis(schedule_analysis):

    schedule_data = schedule_analysis.get(
        "schedule_data",
        []
    )

    critical_path = schedule_analysis.get(
        "critical_path",
        {}
    )


    if not schedule_data:

        return {
            "schedule_health": "UNKNOWN",
            "message": "No schedule data available"
        }


    total_planned = 0
    total_actual = 0
    total_variance = 0

    weighted_planned = 0
    weighted_actual = 0
    total_weight = 0

    for activity in schedule_data:
        planned = activity.get(
            "planned_progress"
        )

        actual = activity.get(
            "actual_progress"
        )

        variance = activity.get(
            "schedule_variance"
        )

        duration = activity.get(
            "duration_days"
        )

        try:
            weight = float(duration or 0)
        except (TypeError, ValueError):
            weight = 0

        if weight < 0:
            weight = 0

        if planned is not None:
            total_planned += planned

            if weight > 0:
                weighted_planned += planned * weight

        if actual is not None:
            total_actual += actual

            if weight > 0:
                weighted_actual += actual * weight

        if variance is not None:
            total_variance += variance

        if weight > 0:
            total_weight += weight

    count = len(schedule_data)

    if total_weight > 0:
        avg_planned = round(
            weighted_planned / total_weight,
            2
        )

        avg_actual = round(
            weighted_actual / total_weight,
            2
        )

        avg_variance = round(
            avg_actual - avg_planned,
            2
        )

    elif count > 0:
        avg_planned = round(
            total_planned / count,
            2
        )

        avg_actual = round(
            total_actual / count,
            2
        )

        avg_variance = round(
            avg_actual - avg_planned,
            2
        )

    else:
        avg_planned = 0
        avg_actual = 0
        avg_variance = 0

    if avg_variance <= -30:
        health = "RED"

    elif avg_variance <= -10:
        health = "YELLOW"

    else:
        health = "GREEN"



    critical_count = critical_path.get(
        "critical_count",
        0
    )


    return {

        "schedule_health": health,

        "planned_progress": avg_planned,

        "actual_progress": avg_actual,

        "schedule_variance": avg_variance,

        "critical_activities": critical_count,

        "critical_path_method":
            critical_path.get(
                "method"
            ),

        "recovery_status":
            "REQUIRED"
            if health in ["RED", "YELLOW"]
            else "MONITOR"

    }
