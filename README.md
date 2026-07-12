# AutoHealOps

AutoHealOps is a self-healing Kubernetes monitoring system that demonstrates how a modern containerized application can be automatically built, tested, monitored, and recovered from failures.

The project combines a React frontend, FastAPI backend, Docker, Kubernetes, Prometheus, Grafana, Alertmanager, GitHub Actions, and Docker Hub.

---

## Project Objective

The main objective of AutoHealOps is to build a cloud-native application that can:

- Automatically build and test code changes.
- Package frontend and backend applications using Docker.
- Store Docker images on Docker Hub.
- Run and manage containers using Kubernetes.
- Maintain application availability using Kubernetes self-healing.
- Monitor Kubernetes and application metrics using Prometheus.
- Visualize monitoring metrics using Grafana.
- Detect system problems using Prometheus alerting rules.
- Display real-time system information using a custom React dashboard.
- Gracefully handle Prometheus connectivity failures.

---

## System Architecture

```text
Developer
    |
    | git push
    v
GitHub Repository
    |
    v
GitHub Actions CI Pipeline
    |
    | Build and Test
    v
Docker Images
    |
    v
Docker Hub
    |
    v
Kubernetes Cluster
    |
    +-------------------------------+
    |                               |
    v                               v
React Frontend Pod          FastAPI Backend Pods
                                    |
                                    v
                               Prometheus
                                    |
                         +----------+----------+
                         |                     |
                         v                     v
                      Grafana             Alertmanager
