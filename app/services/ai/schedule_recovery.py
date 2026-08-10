from app.services.ai.ollama_client import generate


def generate_recovery_plan(schedule_data):

    critical_items = []

    for activity in schedule_data:

        variance = activity.get("schedule_variance")

        if variance is not None and variance < -20:
            critical_items.append(activity)


    if not critical_items:

        return {
            "recovery_required": False,
            "priority": "NORMAL",
            "recommendation": "No recovery action required."
        }


    prompt = f"""
شما مدیر ارشد کنترل پروژه EPC هستید.

برای پروژه EPC زیر یک Recovery Plan مدیریتی تهیه کنید.

اطلاعات فعالیت های بحرانی:

{critical_items}


خروجی شامل:

1- وضعیت فعلی تاخیر

2- علت های محتمل تاخیر:
Engineering
Procurement
Construction
Management


3- اقدامات Recovery Plan:
حداکثر 5 اقدام اجرایی شامل:
- Fast Tracking
- Crashing
- افزایش منابع
- اولویت بندی فعالیت های بحرانی
- جلسات هماهنگی


4- تصمیمات فوری مدیریت:
حداکثر 3 مورد


قوانین:
- فقط تحلیل مدیریتی
- مناسب مدیر پروژه و مدیرعامل
- بدون کدنویسی
- زبان فارسی رسمی
- حداکثر 500 کلمه
"""


    try:

        ai_response = generate(prompt)


    except Exception as e:

        ai_response = (
            "AI در دسترس نیست. "
            "Recovery بر اساس Rule Engine تولید شد. "
            f"فعالیت های بحرانی: {critical_items}"
        )


    return {

        "recovery_required": True,

        "priority": "HIGH",

        "critical_activities": critical_items,

        "recommendation": ai_response

    }