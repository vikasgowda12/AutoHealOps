from fastapi import FastAPI

app = FastAPI(
    title="AutoHealOps API",
    description="Backend service for the AutoHealOps DevOps project",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "AutoHealOps API is running",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }