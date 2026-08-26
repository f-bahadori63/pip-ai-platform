from app.services.ai.ollama_client import generate


def _rule_based_recovery(critical_items):
    """
    Deterministic Recovery Plan.
    This is the guaranteed fallback and must never depend on LLM.
    """

    activities = [
        item.get("activity_name", "Unknown Activity")
        for item in critical_items
    ]

    activity_text = ", ".join(activities)

    return (
        "تاخیر بحرانی در فعالیت‌های زیر شناسایی شده است: "
        f"{activity_text}. "
        "اقدامات فوری شامل بازبینی برنامه تفصیلی، "
        "افزایش منابع در فعالیت بحرانی، بررسی امکان Fast Tracking "
        "و Crashing، اولویت‌دهی به فعالیت‌های بحرانی و برگزاری "
        "جلسه روزانه کنترل برنامه است."
    )


def _build_recovery_plan(critical_items):
    """
    Build deterministic structured Recovery Contract.

    Important:
    This structure does not depend on LLM output.
    """

    activities = []

    for item in critical_items:

        activities.append({
            "activity_name": item.get(
                "activity_name",
                "Unknown Activity"
            ),
            "actual_progress": item.get(
                "actual_progress"
            ),
            "planned_progress": item.get(
                "planned_progress"
            ),
            "schedule_variance": item.get(
                "schedule_variance"
            ),
            "delay_index": item.get(
                "delay_index"
            ),
            "risk_level": item.get(
                "risk_level",
                "HIGH"
            ),
        })

    return {
        "current_status": {
            "status": "DELAYED",
            "severity": "HIGH",
            "critical_activity_count": len(
                critical_items
            ),
            "message": (
                "فعالیت‌های بحرانی پروژه دارای "
                "انحراف منفی از برنامه هستند."
            ),
        },

        "probable_causes": [
            {
                "category": "Procurement",
                "description": (
                    "بررسی تأخیر در تأمین تجهیزات، "
                    "خرید و تعهدات تأمین‌کنندگان."
                )
            },
            {
                "category": "Engineering",
                "description": (
                    "بررسی تأخیر احتمالی در مدارک مهندسی، "
                    "تأییدیه‌ها و اطلاعات موردنیاز خرید."
                )
            },
            {
                "category": "Construction",
                "description": (
                    "بررسی آمادگی منابع و محدودیت‌های اجرایی "
                    "برای فعالیت‌های وابسته."
                )
            },
            {
                "category": "Management",
                "description": (
                    "بررسی تأخیر در تصمیم‌گیری، هماهنگی "
                    "بین واحدها و رفع موانع مدیریتی."
                )
            }
        ],

        "recovery_actions": [
            {
                "priority": 1,
                "action": "Fast Tracking",
                "description": (
                    "بررسی همپوشانی فعالیت‌های قابل اجرا "
                    "برای کاهش مدت باقی‌مانده."
                )
            },
            {
                "priority": 2,
                "action": "Crashing",
                "description": (
                    "ارزیابی افزایش منابع و ظرفیت اجرایی "
                    "در فعالیت بحرانی."
                )
            },
            {
                "priority": 3,
                "action": "Critical Activity Prioritization",
                "description": (
                    "تخصیص اولویت منابع و تصمیمات مدیریتی "
                    "به فعالیت‌های بحرانی."
                )
            },
            {
                "priority": 4,
                "action": "Management Coordination",
                "description": (
                    "برگزاری جلسات کنترل روزانه برای "
                    "رفع موانع و پایش اقدامات Recovery."
                )
            }
        ],

        "management_decisions": [
            {
                "priority": 1,
                "decision": (
                    "تأیید فوری برنامه Recovery برای "
                    "فعالیت‌های بحرانی."
                )
            },
            {
                "priority": 2,
                "decision": (
                    "تعیین مسئول و مهلت مشخص برای "
                    "هر اقدام Recovery."
                )
            }
        ],

        "critical_activities": activities
    }


def generate_recovery_plan(
    schedule_data,
    use_ai=True
):

    critical_items = []

    for activity in schedule_data:

        variance = activity.get(
            "schedule_variance"
        )

        if variance is not None and variance < -20:
            critical_items.append(activity)

    # --------------------------------------------------------
    # NO RECOVERY REQUIRED
    # --------------------------------------------------------

    if not critical_items:

        return {
            "recovery_required": False,
            "priority": "NORMAL",
            "critical_activities": [],
            "recommendation": (
                "No recovery action required."
            ),
            "ai_status": "not_required",
            "recovery_plan": {
                "current_status": {
                    "status": "ON_TRACK",
                    "severity": "NORMAL",
                    "critical_activity_count": 0,
                    "message": (
                        "نیاز فوری به Recovery Plan "
                        "شناسایی نشد."
                    ),
                },
                "probable_causes": [],
                "recovery_actions": [],
                "management_decisions": [],
                "critical_activities": [],
            },
        }

    # --------------------------------------------------------
    # STRUCTURED RECOVERY CONTRACT
    # --------------------------------------------------------

    recovery_plan = _build_recovery_plan(
        critical_items
    )

    # --------------------------------------------------------
    # GUARANTEED RULE-BASED FALLBACK
    # --------------------------------------------------------

    fallback = _rule_based_recovery(
        critical_items
    )

    # --------------------------------------------------------
    # COMPACT AI INPUT
    # --------------------------------------------------------

    compact_items = []

    for activity in critical_items:

        compact_items.append({
            "activity": activity.get(
                "activity_name"
            ),
            "variance": activity.get(
                "schedule_variance"
            ),
            "progress": activity.get(
                "actual_progress"
            ),
            "planned": activity.get(
                "planned_progress"
            ),
        })

    prompt = f"""
شما مدیر ارشد کنترل پروژه EPC هستید.

برای فعالیت‌های بحرانی زیر یک Recovery Plan بسیار کوتاه
و اجرایی برای مدیر پروژه تهیه کنید.

فعالیت‌ها:
{compact_items}

خروجی فقط شامل این موارد باشد:

1. وضعیت تاخیر
2. حداکثر 4 اقدام Recovery
3. حداکثر 2 تصمیم فوری مدیریت

تمرکز بر:
Fast Tracking
Crashing
افزایش منابع
اولویت‌بندی فعالیت بحرانی
هماهنگی مدیریت

زبان فارسی رسمی.
حداکثر 250 کلمه.
"""

    # --------------------------------------------------------
    # DASHBOARD FAST PATH
    # --------------------------------------------------------
    #
    # The Project Control Center must not block on LLM latency.
    # Deterministic recovery data is already available.
    #
    # AI enrichment remains available when use_ai=True.
    # --------------------------------------------------------

    if not use_ai:
        return {
            "recovery_required": True,
            "priority": "HIGH",
            "critical_activities": critical_items,
            "recommendation": fallback,
            "ai_status": "not_requested",
            "recovery_plan": recovery_plan,
        }

    # --------------------------------------------------------
    # AI ENRICHMENT
    # --------------------------------------------------------

    try:

        ai_response = generate(
            prompt,
            timeout=45,
            num_predict=70,
            temperature=0.2,
        )

        if ai_response:

            return {
                "recovery_required": True,
                "priority": "HIGH",
                "critical_activities": critical_items,
                "recommendation": ai_response,
                "ai_status": "completed",
                "recovery_plan": recovery_plan,
            }

    except Exception as exc:

        return {
            "recovery_required": True,
            "priority": "HIGH",
            "critical_activities": critical_items,
            "recommendation": fallback,
            "ai_status": "fallback",
            "ai_error": str(exc),
            "recovery_plan": recovery_plan,
        }

    # --------------------------------------------------------
    # EMPTY AI RESPONSE
    # --------------------------------------------------------

    return {
        "recovery_required": True,
        "priority": "HIGH",
        "critical_activities": critical_items,
        "recommendation": fallback,
        "ai_status": "fallback",
        "recovery_plan": recovery_plan,
    }

