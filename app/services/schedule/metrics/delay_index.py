def calculate_delay_index(activity):
    """
    Canonical PIP Delay Index.

    Definition:
        Delay Index = (Planned Progress - Actual Progress)
                      / Planned Progress

    Interpretation:
        0.00  = on plan
        0.10  = 10% behind plan
        0.25  = 25% behind plan
        0.40  = 40% behind plan
        0.80  = 80% behind plan

    This is a dimensionless ratio.
    Schedule variance remains a percentage-point value and
    must NOT be replaced by this metric.
    """

    planned = activity.get("planned_progress")

    actual = activity.get("actual_progress")

    try:
        planned = float(planned or 0)
    except (TypeError, ValueError):
        planned = 0.0

    try:
        actual = float(actual or 0)
    except (TypeError, ValueError):
        actual = 0.0

    if planned <= 0:
        return 0.0

    delay_index = (
        planned - actual
    ) / planned

    return round(delay_index, 3)
