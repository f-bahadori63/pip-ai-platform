

def calculate_critical_path(activities):

    if not activities:
        return {
            "critical_activities": [],
            "critical_count": 0
        }


    analyzed = []


    for activity in activities:

        duration = activity.duration_days or 0

        start = activity.start_date
        finish = activity.finish_date


        analyzed.append(
            {
                "activity_id": activity.id,
                "activity_code": activity.activity_code,
                "activity_name": activity.activity_name,
                "duration_days": duration,
                "start_date": start,
                "finish_date": finish
            }
        )


    # Temporary CPM logic
    # Full dependency network will be added after WBS integration

    avg_duration = sum(
        item["duration_days"]
        for item in analyzed
    ) / len(analyzed)


    critical = [
        item
        for item in analyzed
        if item["duration_days"] >= avg_duration
    ]


    return {

        "critical_activities": critical,

        "critical_count": len(critical),

        "method":
        "duration_based_cpm_v1"

    }