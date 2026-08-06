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
            "message": "Schedule performance is within acceptable limits."
        }


    prompt = f"""
You are a Senior EPC Project Controls Manager.

Analyze delayed project schedule activities based on PMBOK Schedule Management principles.

Project context:
- Industry: Oil & Gas / EPC
- Project type: Engineering, Procurement, Construction
- Role: Project Controls Manager

Delayed activities:

{critical_items}


Prepare a professional recovery plan in Persian.

Required structure:

1. وضعیت بحرانی برنامه:
- Identify delayed activities
- Explain schedule variance impact

2. تحلیل علت ریشهای:
Classify possible causes:
- Engineering
- Procurement
- Construction
- Resources
- Management decisions

3. برنامه بازیابی زمان:
Provide practical recovery actions:
- Resource increase
- Fast tracking
- Crashing
- Priority adjustment
- Coordination actions

4. تاثیر بر فعالیتهای بعدی:
Explain impact on:
- Procurement
- Construction
- Project completion date

5. اقدامات فوری مدیریت پروه:
Provide a numbered action list.

Use EPC project management terminology.
Do not use generic explanations.
"""


    ai_response = generate(prompt)


    return {

        "recovery_required": True,

        "priority": "HIGH",

        "critical_activities": critical_items,

        "recommendation": ai_response

    }
