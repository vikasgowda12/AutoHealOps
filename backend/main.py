from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import requests

app = FastAPI(
    title="AutoHealOps API",
    description="Backend service for the AutoHealOps DevOps project",
    version="1.0.0"
)

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

PROMETHEUS_URL = "http://127.0.0.1:9090"


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


@app.get("/dashboard")
def dashboard():

    try:
        # Get number of Ready AutoHealOps Pods
        pods_query = (
            'kube_pod_status_ready'
            '{namespace="default", condition="true", '
            'pod=~"autohealops-backend-.*"}'
        )

        pods_response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": pods_query},
            timeout=5
        )

        pods_response.raise_for_status()

        pods_result = pods_response.json()["data"]["result"]

        running_pods = sum(
            int(float(pod["value"][1]))
            for pod in pods_result
        )


        # Get total container restarts
        restarts_query = (
            'sum(kube_pod_container_status_restarts_total'
            '{container="autohealops-backend"})'
        )

        restarts_response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": restarts_query},
            timeout=5
        )

        restarts_response.raise_for_status()

        restarts_result = restarts_response.json()["data"]["result"]

        container_restarts = (
            int(float(restarts_result[0]["value"][1]))
            if restarts_result
            else 0
        )


        # Get active Prometheus alerts
        alerts_query = (
            'ALERTS{'
            'alertstate="firing",'
            'alertname="AutoHealOpsContainerRestarted"'
            '}'
        )

        alerts_response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": alerts_query},
            timeout=5
        )

        alerts_response.raise_for_status()

        alerts_result = alerts_response.json()["data"]["result"]

        active_alerts = len(alerts_result)


        application_status = (
            "Healthy"
            if running_pods > 0
            else "Unhealthy"
        )


        return {
            "application_status": application_status,
            "running_pods": running_pods,
            "container_restarts": container_restarts,
            "active_alerts": active_alerts,
            "prometheus_status": "Connected"
        }


    except requests.RequestException:

        return {
            "application_status": "Unknown",
            "running_pods": 0,
            "container_restarts": 0,
            "active_alerts": 0,
            "prometheus_status": "Disconnected"
        }


Instrumentator().instrument(app).expose(app)