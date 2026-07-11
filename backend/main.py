from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import requests

app = FastAPI(
    title="AutoHealOps API",
    description="Backend service for the AutoHealOps DevOps project",
    version="1.0.0"
)


# Allow frontend applications to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8081"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus URL
PROMETHEUS_URL = "http://127.0.0.1:9090"


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "AutoHealOps CI/CD Pipeline is working",
        "status": "healthy"
    }


# Health endpoint used by Kubernetes
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Dashboard endpoint
@app.get("/dashboard")
def dashboard():

    # -----------------------------------
    # GET NUMBER OF READY PODS
    # -----------------------------------

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


    # -----------------------------------
    # GET CONTAINER RESTARTS
    # -----------------------------------

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


    # -----------------------------------
    # GET ACTIVE PROMETHEUS ALERTS
    # -----------------------------------

    alerts_query = (
        'ALERTS{'
        'alertstate="firing",'
        'alertname="AutoHealOpsContainerRestarted"'
        '}'
    )

    alerts_response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": alerts_query}
    )

    alerts_result = alerts_response.json()["data"]["result"]

    active_alerts = len(alerts_result)


    # -----------------------------------
    # DETERMINE APPLICATION STATUS
    # -----------------------------------

    application_status = (
        "Healthy"
        if running_pods > 0
        else "Unhealthy"
    )


    # -----------------------------------
    # RETURN DASHBOARD DATA
    # -----------------------------------

    return {
        "application_status": application_status,
        "running_pods": running_pods,
        "container_restarts": container_restarts,
        "active_alerts": active_alerts
    }


# Expose FastAPI metrics for Prometheus
Instrumentator().instrument(app).expose(app)