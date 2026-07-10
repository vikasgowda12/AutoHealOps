from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="AutoHealOps API",
    description="Backend service for the AutoHealOps DevOps project",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "AutoHealOps CI/CD Pipeline is working",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Expose application metrics for Prometheus
Instrumentator().instrument(app).expose(app)