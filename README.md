# 🛠️ DevOps Toolkit

![CI/CD](https://github.com/nulldeploy/toolkit/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

CLI-инструмент для системного администрирования, написанный на Python. Проект создан как практическая демонстрация полного DevOps-цикла — от локального скрипта до продакшен деплоя с CI/CD, мониторингом и автоматизацией.

---

## Стек

| Слой | Технологии |
|------|-----------|
| Приложение | Python 3.12, Flask, psutil |
| Контейнеризация | Docker (multi-stage), Docker Compose |
| Веб | Nginx (reverse proxy) |
| CI/CD | GitHub Actions → GHCR → VPS |
| Оркестрация | Kubernetes (Deployment, Service, Ingress) |
| Автоматизация | Ansible (см. [toolkit-infra](https://github.com/nulldeploy/toolkit-infra)) |
| Мониторинг | Prometheus, Grafana, Loki, Alertmanager (см. [toolkit-monitoring](https://github.com/nulldeploy/toolkit-monitoring)) |

---

## Архитектура

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

## Команды

| Команда | Описание |
|---------|----------|
| `scan` | Сканирует директорию: статистика, топ N файлов по размеру |
| `backup` | Создаёт архив директории с автоматической ротацией |
| `monitor` | Мониторинг CPU, RAM, диска в реальном времени |
| `deploy` | Git pull + перезапуск systemd сервиса |
| `serve` | Запускает Flask сервер с `/health` эндпоинтом |

---

## Быстрый старт

### Docker Compose

```bash
git clone https://github.com/nulldeploy/toolkit.git
cd toolkit
cp .env.example .env
docker compose up -d
curl http://localhost/health
```

### Локально

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

## Примеры

```bash
# Сканирование с топ 10 файлов в JSON формате
python toolkit.py scan ~/projects --top 10 --format json

# Бэкап в zip с хранением последних 3 архивов
python toolkit.py backup ~/projects ~/backups --ext zip --keep 3

# Мониторинг с обновлением каждые 5 секунд и логированием
python toolkit.py monitor --watch 5 --log monitor.log

# Деплой из ветки develop с перезапуском nginx
python toolkit.py deploy ~/projects --branch develop --restart nginx
```

---

## CI/CD пайплайн

```
push to main
    │
    ├── job: test
    │     ├── ruff check .        (линтер)
    │     └── pytest tests/ -v    (тесты)
    │
    └── job: build (только если test прошёл)
          ├── docker build
          ├── push → ghcr.io/nulldeploy/toolkit:sha-xxxxx
          ├── push → ghcr.io/nulldeploy/toolkit:latest
          └── ssh → VPS
                    ├── docker compose pull
                    └── docker compose up -d
```

---

## Структура проекта

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

## Инфраструктура

**Docker** — multi-stage сборка: зависимости устанавливаются в builder-слое, финальный образ на `python:3.12-slim`. Non-root пользователь, healthcheck через `/health`.

**Docker Compose** — два сервиса: приложение и nginx как reverse proxy, изолированная Docker-сеть.

**GitHub Actions** — линтер `ruff` и тесты на каждый push в `main`. При успехе — сборка образа, пуш в GHCR, автодеплой на VPS через SSH.

**Kubernetes** — Deployment с readiness/liveness пробами, Service (ClusterIP), Ingress с маршрутизацией по хосту.

**Ansible** — полная автоматизация деплоя на чистый VPS: UFW, Docker, nginx, systemd, Node Exporter. Один запуск плейбука разворачивает весь стек. Подробнее: [toolkit-infra](https://github.com/nulldeploy/toolkit-infra).

---

## Конфигурация

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

## systemd (ручной деплой)

```bash
sudo cp toolkit.service.example /etc/systemd/system/toolkit.service
# отредактируй User и WorkingDirectory
sudo systemctl daemon-reload
sudo systemctl enable toolkit
sudo systemctl start toolkit
journalctl -u toolkit -f
```