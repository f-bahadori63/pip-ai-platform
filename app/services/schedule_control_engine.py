from datetime import datetime


def calculate_schedule_status(activity):

    result = {
        "activity_id": activity.id,
        "activity_code": activity.activity_code,
        "activity_name": activity.activity_name,
        "duration_days": activity.duration_days,
        "actual_progress": activity.progress_percent,
        "status": activity.status,
    }


    # اگر تاریخ شروع یا مدت وجود ندارد
    if not activity.start_date or not activity.duration_days:

        result.update(
            {
                "planned_progress": None,
                "schedule_variance": None,
                "delay_index": None,
                "risk_level": "UNKNOWN"
            }
        )

        return result


    today = datetime.utcnow()


    elapsed_days = (
        today - activity.start_date
    ).days


    if elapsed_days < 0:
        elapsed_days = 0


    planned_progress = (
        elapsed_days /
        activity.duration_days
    ) * 100


    if planned_progress > 100:
        planned_progress = 100


    actual_progress = (
        activity.progress_percent
        or 0
    )


    schedule_variance = (
        actual_progress -
        planned_progress
    )


    if planned_progress > 0:

        delay_index = (
            planned_progress -
            actual_progress
        ) / planned_progress

    else:

        delay_index = 0



    if delay_index < 0.1:

        risk_level = "LOW"

    elif delay_index < 0.25:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"



    result.update(
        {
            "planned_progress":
                round(planned_progress,2),

            "schedule_variance":
                round(schedule_variance,2),

            "delay_index":
                round(delay_index,3),

            "risk_level":
                risk_level
        }
    )


    return result