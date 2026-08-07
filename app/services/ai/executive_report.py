def generate_executive_report(
    schedule_analysis,
    kpis,
    alerts
):

    return {

        "report_type": "Executive Status Report",

        "status": kpis.get(
            "schedule_health",
            "UNKNOWN"
        ),

        "summary": (
            "گزارش مدیریتی اولیه پروژه تولید شد. "
            "پروژه از نظر کنترل زمان نیازمند توجه مدیریتی است."
        ),

        "kpis": kpis,

        "alerts": alerts

    }