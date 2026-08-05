from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.ai.ollama_client import generate
from app.services.ai.project_assistant import build_project_summary

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
def local_chat(prompt: str = Query(...)):
    response = generate(prompt)

    return {
        "model": "qwen2.5:3b",
        "response": response,
        "done": True,
    }


@router.get("/project-summary/{project_id}")
def project_summary(project_id: int, db: Session = Depends(get_db)):
    return build_project_summary(db, project_id)
