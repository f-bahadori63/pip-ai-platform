from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.projects import router as project_router

app = FastAPI(
    title="PIP AI Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)

@app.get("/")
def root():
    return {
        "system": "PIP AI Platform",
        "status": "running"
    }