import json
from typing import Any

from sqlalchemy.orm import Session

from app.services.ai.project_control_center import build_project_control_center


def _get(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _compact_activity(activity: Any) -> dict:
    return {
        "name": _get(activity, "activity_name", ""),
        "actual": _get(activity, "actual_progress", 0),
        "planned": _get(activity, "planned_progress", 0),
        "variance": _get(activity, "schedule_variance", 0),
        "delay_index": _get(activity, "delay_index", 0),
        "risk": _get(activity, "risk_level", ""),
    }


def _select_critical_activities(schedule: Any) -> list:
    activities = _get(schedule, "schedule_data", []) or []

    normalized = [
        _compact_activity(activity)
        for activity in activities
    ]

    high_risk = [
        activity
        for activity in normalized
        if str(activity.get("risk", "")).upper() == "HIGH"
    ]

    if high_risk:
        activities = high_risk
    else:
        activities = normalized

    activities.sort(
        key=lambda x: float(x.get("variance", 0) or 0)
    )

    return activities[:3]


def _compact_alerts(alerts: Any) -> list:
    if not alerts:
        return []

    result = []

    for alert in alerts[:3]:
        result.append({
            "level": _get(alert, "level", ""),
            "title": _get(alert, "title", ""),
            "action": _get(alert, "action", ""),
        })

    return result


def build_project_ai_context(
    db: Session,
    project_id: int,
    user_question: str = "",
) -> dict:

    control_center = build_project_control_center(
        db,
        project_id
    )

    if not control_center:
        return {
            "error": "Project context unavailable"
        }

    if isinstance(control_center, dict):
        if control_center.get("error"):
            return control_center

    schedule = _get(control_center, "schedule", {}) or {}
    kpis = _get(control_center, "kpis", {}) or {}
    costs = _get(control_center, "costs", {}) or {}
    alerts = _get(control_center, "alerts", []) or {}
    recovery = _get(control_center, "recovery", {}) or {}

    critical_activities = _select_critical_activities(
        schedule
    )

    compact = {
        "project_id": project_id,
        "overall_status": _get(
            control_center,
            "status",
            "UNKNOWN"
        ),

        "schedule": {
            "health": _get(
                kpis,
                "schedule_health",
                _get(control_center, "status", "UNKNOWN")
            ),
            "planned_progress": _get(
                kpis,
                "planned_progress",
                None
            ),
            "actual_progress": _get(
                kpis,
                "actual_progress",
                None
            ),
            "variance": _get(
                kpis,
                "schedule_variance",
                None
            ),
            "critical_activities": _get(
                kpis,
                "critical_activities",
                0
            ),
            "risk_level": _get(
                schedule,
                "risk_level",
                "UNKNOWN"
            ),
            "recovery_required": _get(
                recovery,
                "recovery_required",
                False
            ),
        },

        "critical_activities": critical_activities,

        "cost": {
            "health": _get(
                costs,
                "cost_health",
                "UNKNOWN"
            ),
            "planned": _get(
                costs,
                "planned_cost",
                None
            ),
            "actual": _get(
                costs,
                "actual_cost",
                None
            ),
            "earned_value": _get(
                costs,
                "earned_value",
                None
            ),
            "variance": _get(
                costs,
                "cost_variance",
                None
            ),
        },

        "alerts": _compact_alerts(alerts),

        "recovery": {
            "required": _get(
                recovery,
                "recovery_required",
                False
            ),
            "priority": _get(
                recovery,
                "priority",
                "NORMAL"
            ),
        },
    }

    return compact


def build_ai_prompt(
    context: dict,
    question: str,
) -> str:

    context_json = json.dumps(
        context,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )

    return f"""
شما دستیار هوشمند مدیریت پروژه PIP و متخصص پروژه‌های EPC هستید.

قوانین:
- فقط بر اساس Context پروژه پاسخ بده.
- عدد یا وضعیت پروژه را تغییر نده.
- اگر داده‌ای وجود ندارد، بگو اطلاعات آن موجود نیست.
- پاسخ کوتاه، دقیق و اجرایی باشد.
- از حدس زدن اطلاعات پروژه خودداری کن.
- زبان پاسخ مطابق زبان سؤال باشد.

PROJECT CONTEXT:
{context_json}

USER QUESTION:
{question}

پاسخ مدیریتی:
""".strip()
