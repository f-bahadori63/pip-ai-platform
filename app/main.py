from fastapi import FastAPI

app = FastAPI(
    title="PIP AI Platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "system": "PIP AI Platform",
        "status": "running"
    }