# 🛠️ DevOps Toolkit

![CI/CD](https://github.com/nulldeploy/toolkit/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

A CLI tool for system administration built with Python. This project demonstrates a full DevOps cycle — from a local script to a production deployment with CI/CD, monitoring, and infrastructure automation.

---

## Stack

| Layer | Technologies |
|-------|-------------|
| Application | Python 3.12, Flask, psutil |
| Containerization | Docker (multi-stage), Docker Compose |
| Web | Nginx (reverse proxy) |
| CI/CD | GitHub Actions → GHCR → VPS |
| Orchestration | Kubernetes (Deployment, Service, Ingress) |
| Automation | Ansible (see [toolkit-infra](https://github.com/nulldeploy/toolkit-infrastructure)) |
| Monitoring | Prometheus, Grafana, Loki, Alertmanager (see [toolkit-monitoring](https://github.com/nulldeploy/toolkit-monitoring)) |

---

## Architecture

```
git push → GitHub Actions
              ├── ruff lint
              ├── pytest
              └── docker build → push → GHCR
                                          │
                                          ▼
                                        VPS
                                   docker compose pull
                                   docker compose up -d
                                          │
                                   ┌──────┴──────┐
                                   │    nginx    │ :80
                                   └──────┬──────┘
                                          │
                                   ┌──────┴──────┐
                                   │   toolkit   │ :5000
                                   └─────────────┘
```

---

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scans a directory: file stats, top N files by size |
| `backup` | Creates a directory archive with automatic rotation |
| `monitor` | Real-time CPU, RAM, and disk monitoring |
| `deploy` | Git pull + systemd service restart |
| `serve` | Starts a Flask server with `/health` endpoint |

---

## Quick Start

### Docker Compose

```bash
git clone https://github.com/nulldeploy/toolkit.git
cd toolkit
cp .env.example .env
docker compose up -d
curl http://localhost/health
```

### Local

```bash
pip install -r requirements.txt
python toolkit.py scan ~/projects
python toolkit.py backup ~/projects ~/backups --keep 5
python toolkit.py monitor --watch 3
python toolkit.py deploy ~/projects --restart nginx
```

### Docker

```bash
docker build -t toolkit .
docker run toolkit scan /path/to/dir
docker run toolkit monitor
```

---

## Usage Examples

```bash
# Scan with top 10 files in JSON format
python toolkit.py scan ~/projects --top 10 --format json

# Backup to zip, keep last 3 archives
python toolkit.py backup ~/projects ~/backups --ext zip --keep 3

# Monitor with 5-second interval and file logging
python toolkit.py monitor --watch 5 --log monitor.log

# Deploy from develop branch with nginx restart
python toolkit.py deploy ~/projects --branch develop --restart nginx
```

---

## CI/CD Pipeline

```
push to main
    │
    ├── job: test
    │     ├── ruff check .        (linter)
    │     └── pytest tests/ -v    (tests)
    │
    └── job: build (runs only if test passed)
          ├── docker build
          ├── push → ghcr.io/nulldeploy/toolkit:sha-xxxxx
          ├── push → ghcr.io/nulldeploy/toolkit:latest
          └── ssh → VPS
                    ├── docker compose pull
                    └── docker compose up -d
```

---

## Project Structure

```
toolkit/
├── .github/
│   └── workflows/
│       └── ci.yml              # lint → test → build → deploy
├── commands/
│   ├── scan.py
│   ├── backup.py
│   ├── monitor.py
│   ├── deploy.py
│   └── serve.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── nginx/
│   └── nginx.conf
├── tests/
│   └── test_basic.py
├── toolkit.py
├── Dockerfile
├── docker-compose.yml
├── toolkit.service.example
├── .env.example
└── requirements.txt
```

---

## Infrastructure

**Docker** — multi-stage build: dependencies are installed in the builder stage, final image uses `python:3.12-slim`. Non-root user, healthcheck via `/health`.

**Docker Compose** — two services: application and nginx as reverse proxy, isolated Docker network.

**GitHub Actions** — `ruff` linter and tests on every push to `main`. On success — builds image, pushes to GHCR, auto-deploys to VPS via SSH.

**Kubernetes** — Deployment with readiness/liveness probes, Service (ClusterIP), Ingress with host-based routing.

**Ansible** — full deployment automation on a clean VPS: UFW, Docker, nginx, systemd, Node Exporter. One playbook run sets up the entire stack. See [toolkit-infra](https://github.com/nulldeploy/toolkit-infrastructure).

---

## Configuration

```bash
cp .env.example .env
```

```env
APP_PORT=5000
```

---

## Kubernetes

```bash
minikube start
kubectl apply -f k8s/
kubectl get pods
kubectl get svc
kubectl logs <pod-name>
```

---

## systemd (manual deploy)

```bash
sudo cp toolkit.service.example /etc/systemd/system/toolkit.service
# edit User and WorkingDirectory
sudo systemctl daemon-reload
sudo systemctl enable toolkit
sudo systemctl start toolkit
journalctl -u toolkit -f
```
