# 🛠️ DevOps Toolkit

![CI/CD](https://github.com/nulldeploy/toolkit/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

CLI инструмент для системного администрирования и мониторинга. Написан на Python, задеплоен с полным DevOps стеком — Docker, nginx, systemd, GitHub Actions CI/CD, Kubernetes.

---

## Команды

| Команда | Описание |
|---|---|
| `scan` | Сканирует директорию и выводит статистику |
| `backup` | Создаёт архив директории с ротацией |
| `monitor` | Мониторинг системы в реальном времени |
| `deploy` | Git pull + перезапуск сервиса |
| `serve` | Запускает Flask сервер с `/health` эндпоинтом |

---

## Быстрый старт

### Docker

```bash
docker build -t toolkit .
docker run toolkit scan /path/to/dir
docker run toolkit monitor
```

### Docker Compose

```bash
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

## Структура проекта

```
toolkit/
├── .github/
│   └── workflows/
│       └── ci.yml          # lint → test → build
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

**Docker** — multi-stage сборка, минимальный образ `python:3.12-slim`, non-root пользователь, healthcheck.

**Docker Compose** — два сервиса: приложение и nginx как reverse proxy, изолированная сеть.

**systemd** — автозапуск через `docker compose up`, шаблон юнита в `toolkit.service.example`.

**GitHub Actions** — линтер `ruff` + тесты на каждый push, сборка и пуш образа в GHCR при merge в `main`.

**Kubernetes** — Deployment с readiness/liveness пробами, Service (ClusterIP), Ingress с маршрутизацией по хосту.

---

## Конфигурация

Скопируй `.env.example` в `.env` и заполни:

```bash
cp .env.example .env
```

```env
APP_PORT=5000
```

---

## systemd (продакшн)

```bash
sudo cp toolkit.service.example /etc/systemd/system/toolkit.service
# отредактируй User, WorkingDirectory
sudo systemctl enable toolkit
sudo systemctl start toolkit
journalctl -u toolkit -f
```

---

## Kubernetes

```bash
minikube start
kubectl apply -f k8s/
kubectl get pods
kubectl logs <pod-name>
```