import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.data_import.schedule_importer import import_schedule_excel
from app.services.project_file_resolver import (
    project_resolution_payload,
    resolve_project_from_filename,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


def _extract_pdf_text(file_path: str) -> tuple[str, int]:
    reader = PdfReader(file_path)
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages), len(reader.pages)


def _build_management_prompt(
    filename: str,
    project_id: int,
    content: str,
    file_type: str,
) -> str:
    return f"""
You are the PIP AI Platform Management Intelligence Engine.

Project ID: {project_id}
Input file: {filename}
Input type: {file_type}

Analyze the supplied project information as an EPC project management expert.

Produce a concise management-oriented output containing:

1. Executive Summary
2. Current Project Situation
3. Key Findings
4. Schedule / Progress Issues
5. Cost or Commercial Issues if identifiable
6. Risks and Critical Concerns
7. Management Actions
8. Priority Actions
9. Missing / Uncertain Information

Do not invent facts.
Clearly distinguish calculated/observed information from assumptions.
Focus on information useful to a Project Manager and senior management.

INPUT:
{content}
"""


def _call_existing_ai(prompt: str):
    from app.services.ai.schedule_analyzer import ScheduleAnalyzer

    analyzer = ScheduleAnalyzer()

    for method_name in ["analyze_text", "analyze", "run"]:
        method = getattr(analyzer, method_name, None)

        if callable(method):
            try:
                return method(prompt)
            except TypeError:
                continue

    raise RuntimeError(
        "Existing AI schedule analyzer does not expose a compatible "
        "text-analysis method"
    )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    # Retained for API compatibility. Filename resolution is authoritative.
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    filename = file.filename or ""
    lower_name = filename.lower()

    if not lower_name.endswith((".xlsx", ".xls", ".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel (.xlsx/.xls) and PDF files are allowed"
        )

    try:
        project, project_created = resolve_project_from_filename(db, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project_payload = project_resolution_payload(project, project_created)
    resolved_project_id = project.id
    suffix = os.path.splitext(filename)[1].lower()
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        if suffix in (".xlsx", ".xls"):
            result = import_schedule_excel(
                db=db,
                file_path=temp_path,
                project_id=resolved_project_id,
            )

            imported = bool(result.get("imported", False))

            if not imported and project_created:
                db.rollback()

            return {
                "status": "completed" if imported else result.get("status"),
                "input_type": "excel",
                "filename": filename,
                "project_id": project_payload["id"],
                "project": project_payload,
                "requested_project_id": project_id,
                "import": result,
                "management_intelligence": (
                    {
                        "status": "available",
                        "source": "project_schedule",
                        "next_endpoint": (
                            "/ai/project-control-center/"
                            f"{resolved_project_id}"
                        ),
                    }
                    if imported
                    else {
                        "status": "not_generated",
                        "reason": "Schedule normalization did not complete",
                    }
                ),
            }

        pdf_text, page_count = _extract_pdf_text(temp_path)

        if not pdf_text.strip():
            raise HTTPException(
                status_code=422,
                detail="PDF contains no extractable text"
            )

        prompt = _build_management_prompt(
            filename=filename,
            project_id=resolved_project_id,
            content=pdf_text[:120000],
            file_type="PDF",
        )

        try:
            ai_result = _call_existing_ai(prompt)
        except Exception as exc:
            ai_result = {
                "status": "pending",
                "message": (
                    "PDF extracted successfully; existing AI engine requires "
                    "a compatible text-analysis interface."
                ),
                "error": str(exc),
            }

        db.commit()

        return {
            "status": "completed",
            "input_type": "pdf",
            "filename": filename,
            "project_id": resolved_project_id,
            "project": project_payload,
            "requested_project_id": project_id,
            "pages_text_extracted": page_count,
            "text_length": len(pdf_text),
            "extracted_text": pdf_text,
            "management_intelligence": ai_result,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
