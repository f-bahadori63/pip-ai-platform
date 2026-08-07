from fastapi import FastAPI
from app.routers.contracts import router as contract_router
from app.routers.projects import router as project_router
from app.routers.wbs import router as wbs_router
from app.routers.ai import router as ai_router
from app.routers.risks import router as risks_router
from app.routers.schedule import router as schedule_router
from app.routers.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="PIP AI Platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(contract_router)
app.include_router(project_router)
app.include_router(wbs_router)
app.include_router(ai_router)
app.include_router(risks_router)
app.include_router(schedule_router)
app.include_router(dashboard_router)
@app.get("/")
def root():
    return {
        "system": "PIP AI Platform",
        "status": "running"
    }
