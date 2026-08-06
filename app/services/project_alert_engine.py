def generate_project_alerts(kpis):

    alerts = []


    schedule_health = kpis.get(
        "schedule_health"
    )

    variance = kpis.get(
        "schedule_variance"
    )

    recovery_status = kpis.get(
        "recovery_status"
    )


    if variance is not None:

        if variance <= -30:

            alerts.append(
                {
                    "level": "CRITICAL",
                    "title": "Schedule Delay Detected",
                    "message": f"Project is {abs(variance)}% behind planned progress",
                    "action": "Execute Recovery Plan"
                }
            )

        elif variance <= -10:

            alerts.append(
                {
                    "level": "WARNING",
                    "title": "Schedule Variance Warning",
                    "message": f"Schedule variance is {variance}%",
                    "action": "Monitor and prepare mitigation plan"
                }
            )


    if schedule_health == "RED":

        alerts.append(
            {
                "level": "CRITICAL",
                "title": "Project Schedule Health RED",
                "message": "Project requires management attention",
                "action": "Review recovery actions"
            }
        )


    if recovery_status == "REQUIRED":

        alerts.append(
            {
                "level": "ACTION_REQUIRED",
                "title": "Recovery Plan Required",
                "message": "Delayed activities need corrective actions",
                "action": "Initiate recovery workflow"
            }
        )


    return alerts
