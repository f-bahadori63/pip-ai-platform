from app.services.ai.ollama_client import generate


def generate_project_summary(dashboard_data: dict) -> str:

    prompt = f"""
You are an EPC Project Control Manager.

Analyze the following project dashboard data.

Rules:
- Write maximum 5 sentences.
- Mention project status.
- Mention progress variance.
- Mention critical issues.
- Suggest management action.
- Do not invent information.

Dashboard Data:
{dashboard_data}
"""

    return generate(prompt)
