from app.services.ai.ollama_client import generate


def generate_executive_report(
    schedule_analysis,
    kpis,
    alerts
):

    prompt = f"""
You are a Senior EPC Project Manager preparing an Executive Status Report.

Project Control Data:

Schedule Analysis:
{schedule_analysis}

KPI Status:
{kpis}

Management Alerts:
{alerts}


Prepare a professional executive project report in Persian.

Report structure:

1. وضعیت کلی پروه
- Overall project health
- Schedule status
- Risk level

2. شاخصهای کلیدی پروه:
- Planned Progress
- Actual Progress
- Schedule Variance
- Delay Index

3. مسائل بحرانی:
- Identify major problems
- Explain project impact

4. اقدامات پیشنهادی مدیریت:
- Immediate actions
- Recovery actions
- Required decisions

5. جمعبندی مدیریتی:
Provide a concise executive conclusion suitable for project steering committee.

Use EPC, PMBOK and project controls terminology.
Avoid generic explanations.
"""


    response = generate(prompt)


    return {

        "report_type": "Executive Status Report",

        "status": kpis.get(
            "schedule_health",
            "UNKNOWN"
        ),

        "summary": response,

        "kpis": kpis,

        "alerts": alerts

    }
