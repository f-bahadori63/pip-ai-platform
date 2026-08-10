def calculate_delay_index(activity):

    planned = activity.get(
        "planned_progress",
        0
    )

    actual = activity.get(
        "actual_progress",
        0
    )

    if planned == 0:
        return 0


    delay_index = (
        (actual - planned)
        /
        planned
    ) * 100


    return round(
        delay_index,
        2
    )