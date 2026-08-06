from app.services.ai.schedule_analyzer import analyze_project_schedule
from app.services.ai.schedule_recovery import generate_recovery_plan
from app.services.project_control_kpi import calculate_project_kpis
from app.services.project_alert_engine import generate_project_alerts
from app.services.ai.executive_report import generate_executive_report


def build_project_control_center(
    db,
    project_id: int
):

    schedule_analysis = analyze_project_schedule(
        db,
        project_id
    )


    kpis = calculate_project_kpis(
        schedule_analysis
    )


    alerts = generate_project_alerts(
        kpis
    )


    recovery = generate_recovery_plan(
        schedule_analysis.get(
            "schedule_data",
            []
        )
    )


    executive_report = generate_executive_report(
        schedule_analysis,
        kpis,
        alerts
    )


    return {

        "project_id": project_id,

        "status":
            kpis.get(
                "schedule_health",
                "UNKNOWN"
            ),

        "schedule": schedule_analysis,

        "kpis": kpis,

        "alerts": alerts,

        "recovery": recovery,

        "executive_report": executive_report

    }
