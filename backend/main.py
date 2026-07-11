from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import requests

app = FastAPI(
    title="AutoHealOps API",
    description="Backend service for the AutoHealOps DevOps project",
    version="1.0.0"
)


# Allow React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus URL
PROMETHEUS_URL = "http://127.0.0.1:9090"


@app.get("/")
def home():
    return {
        "message": "AutoHealOps CI/CD Pipeline is working",
        "status": "healthy"
    }


# Healthy endpoint for Kubernetes probes
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/dashboard")
def dashboard():

    # Get the real number of READY AutoHealOps Pods
    pods_query = (
        'kube_pod_status_ready'
        '{namespace="default", condition="true", '
        'pod=~"autohealops-backend-.*"}'
    )

    pods_response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": pods_query}
    )

    pods_result = pods_response.json()["data"]["result"]

    running_pods = sum(
        int(float(pod["value"][1]))
        for pod in pods_result
    )


    # Get total AutoHealOps container restarts
    restarts_query = (
        'sum(kube_pod_container_status_restarts_total'
        '{container="autohealops-backend"})'
    )

    restarts_response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": restarts_query}
    )

    restarts_result = restarts_response.json()["data"]["result"]

    container_restarts = (
        int(float(restarts_result[0]["value"][1]))
        if restarts_result
        else 0
    )


    # Get active AutoHealOps alerts
    alerts_query = (
        'ALERTS{alertstate="firing",'
        'alertname="AutoHealOpsContainerRestarted"}'
    )

    alerts_response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": alerts_query}
    )

    alerts_result = alerts_response.json()["data"]["result"]

    active_alerts = len(alerts_result)


    # Determine application status
    application_status = (
        "Healthy"
        if running_pods > 0
        else "Unhealthy"
    )


    return {
        "application_status": application_status,
        "running_pods": running_pods,
        "container_restarts": container_restarts,
        "active_alerts": active_alerts
    }


# Expose application metrics for Prometheus
Instrumentator().instrument(app).expose(app)