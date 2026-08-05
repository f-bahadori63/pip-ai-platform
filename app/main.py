from fastapi import FastAPI
from app.routers.contracts import router as contract_router
from app.routers.projects import router as project_router
from app.routers.wbs import router as wbs_router
from app.routers.ai import router as ai_router

app = FastAPI(
    title="PIP AI Platform",
    version="1.0.0"
)
app.include_router(contract_router)
app.include_router(project_router)
app.include_router(wbs_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {
        "system": "PIP AI Platform",
        "status": "running"
    }