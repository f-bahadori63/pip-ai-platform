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


        if planned is not None:
            total_planned += planned


        if actual is not None:
            total_actual += actual


        if variance is not None:
            total_variance += variance



    count = len(schedule_data)


    avg_planned = round(
        total_planned / count,
        2
    )


    avg_actual = round(
        total_actual / count,
        2
    )


    avg_variance = round(
        total_variance / count,
        2
    )


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