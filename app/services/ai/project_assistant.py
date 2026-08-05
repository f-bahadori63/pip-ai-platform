from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.wbs import WBSItem
from app.models.risk import Risk
from app.services.ai.ollama_client import generate


def build_project_summary(db: Session, project_id: int) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return {"error": "Project not found"}

    # WBS
    wbs_items = (
        db.query(WBSItem)
        .filter(WBSItem.project_id == project_id)
        .all()
    )

    wbs_text = "\n".join(
        f"- {item.code} | {item.name}"
        for item in wbs_items
    )

    # Risks
    risks = (
        db.query(Risk)
        .filter(Risk.project_id == project_id)
        .order_by(Risk.score.desc())
        .all()
    )

    risk_text = "\n".join(
        f"- {r.risk_code} | {r.title} | Score={r.score} | Status={r.status}"
        for r in risks
    )

    prompt = f"""
شما دستیار مدیریت پروژه PIP و متخصص پروژه‌های EPC نفت، گاز، پتروشیمی و فولاد هستید.

اطلاعات پروژه:

کد پروژه: {project.project_code}
نام پروژه: {project.name}
کارفرما: {project.client}
وضعیت: {project.status}

ساختار WBS:

{wbs_text if wbs_text else 'هیچ آیتمی ثبت نشده است.'}

ریسک‌های ثبت‌شده پروژه:

{risk_text if risk_text else 'هیچ ریسکی ثبت نشده است.'}

در قالب یک گزارش حرفه‌ای EPC حداکثر در 10 خط موارد زیر را ارائه کن:

1. خلاصه وضعیت فعلی پروژه
2. وضعیت ساختار WBS
3. سه ریسک بحرانی پروژه به ترتیب اولویت
4. اثر احتمالی ریسک‌ها بر زمان و هزینه پروژه
5. پیشنهاد فوری مدیر پروژه برای کاهش ریسک
6. سطح سلامت کلی پروژه (Green / Yellow / Red)

پاسخ باید کوتاه، اجرایی و مناسب ارائه به مدیرعامل یا PMO باشد.
"""

    ai_response = generate(prompt)

    return {
        "project_id": project.id,
        "project_code": project.project_code,
        "project_name": project.name,
        "summary": ai_response,
    }