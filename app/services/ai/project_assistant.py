from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.wbs import WBSItem
from app.models.contract import Contract

from app.services.ai.ollama_client import generate


def build_project_summary(db: Session, project_id: int) -> dict:

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return {"error": "Project not found"}

    wbs_items = (
        db.query(WBSItem)
        .filter(WBSItem.project_id == project_id)
        .all()
    )

    contract = (
        db.query(Contract)
        .filter(Contract.project_id == project_id)
        .first()
    )

    wbs_text = "\n".join(
        f"- {item.code} | {item.name}"
        for item in wbs_items
    )

    contract_text = "قراردادی ثبت نشده است."

    if contract:
        contract_text = f"""
شماره قرارداد: {contract.contract_number}
کارفرما: {contract.client}
پیمانکار: {contract.contractor}
نوع قرارداد: {contract.contract_type}
مبلغ قرارداد: {contract.contract_value} {contract.currency}
تاریخ شروع: {contract.start_date}
تاریخ پایان: {contract.end_date}
شرح قرارداد: {contract.description}
"""

    prompt = f"""
شما دستیار هوشمند مدیریت پروژه PIP هستید.

اطلاعات پروژه:

کد پروژه:
{project.project_code}

نام پروژه:
{project.name}

وضعیت پروژه:
{project.status}


اطلاعات قرارداد:

{contract_text}


ساختار WBS:

{wbs_text if wbs_text else "هیچ WBS ثبت نشده است."}


یک گزارش مدیریتی در ۵ بخش ارائه کن:

1- خلاصه وضعیت فعلی پروژه
2- تحلیل قرارداد و اثر آن بر اجرا:
- بررسی نوع قرارداد (EPC، Lump Sum، Cost Plus و ...)
- بررسی مبلغ و ارز قرارداد
- بررسی مدت قرارداد
- شناسایی ریسک‌های مالی، ارزی و زمانی
- بررسی وجود یا عدم وجود بند تعدیل قیمت
- بررسی اثر شرایط قراردادی بر مدیریت پروژه
3- وضعیت ساختار شکست کار WBS
4- مهم‌ترین ریسک‌های پروژه
5- پیشنهاد اقدام بعدی مدیر پروژه

پاسخ باید مانند گزارش یک مدیر پروژه ارشد EPC نوشته شود.
از کلی‌گویی خودداری کن.
بر اساس داده‌های واقعی پروژه تحلیل ارائه بده.
"""

    ai_response = generate(prompt)

    return {
        "project_id": project.id,
        "project_code": project.project_code,
        "project_name": project.name,
        "summary": ai_response,
    }