import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.ai import router as ai_router
from app.routers.analysis import router as analysis_router
from app.routers.contracts import router as contract_router
from app.routers.cost import router as cost_router
from app.routers.dashboard import router as dashboard_router
from app.routers.demo.router import router as demo_router
from app.routers.documents import router as documents_router
from app.routers.projects import router as project_router
from app.routers.risk_register.risk_register import router as risk_register_router
from app.routers.risks import router as risks_router
from app.routers.schedule import router as schedule_router
from app.routers.schedule_import import router as schedule_import_router
from app.routers.wbs import router as wbs_router

app = FastAPI(
    title="PIP AI Platform",
    version="1.0.0",
    default_response_class=JSONResponse
)

# PIP MVP required routers
app.include_router(project_router)
app.include_router(documents_router)

# PIP MVP router registration - module scope
app.include_router(contract_router)
app.include_router(wbs_router)
app.include_router(ai_router)
app.include_router(risks_router)
app.include_router(schedule_router)
app.include_router(schedule_import_router)
app.include_router(dashboard_router)
app.include_router(cost_router)
app.include_router(risk_register_router)
app.include_router(demo_router)
app.include_router(analysis_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_utf8_header(request, call_next):

    response = await call_next(request)

    content_type = response.headers.get("content-type", "")

    if content_type.startswith("application/json") and "charset=" not in content_type:
        response.headers["content-type"] = "application/json; charset=utf-8"

    return response
@app.get("/")
def root():
    return {
        "system": "PIP AI Platform",
        "status": "running"
    }
