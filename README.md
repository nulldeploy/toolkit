# DevOps Toolkit — Portfolio Project

## Цель
Задеплоить toolkit как полноценный DevOps проект.
Каждый этап — отдельный коммит в git.

---

## Этап 1 — Docker

Упаковать toolkit в Docker образ.

**Требования:**
- базовый образ — `python:3.12-slim`
- зависимости установлены через `requirements.txt`
- образ запускается как CLI инструмент
- аргументы передаются при запуске контейнера

**Результат:**
```bash
docker build -t toolkit .
docker run toolkit scan /path
docker run toolkit backup /src /dst --keep 5
docker run toolkit monitor
```

---

## Этап 2 — Docker Compose + nginx

Добавить `docker-compose.yml` и nginx как reverse proxy.

> [!note] Для CLI инструмента nginx не нужен по смыслу.
> Но цель — практика. Добавь простой веб-эндпоинт в toolkit
> (например Flask `/health` который возвращает статус системы),
> и поставь nginx перед ним.

**Требования:**
- `docker-compose.yml` с двумя сервисами: `toolkit` и `nginx`
- nginx проксирует запросы на toolkit
- конфиг nginx в отдельном файле `nginx/nginx.conf`
- сервисы поднимаются одной командой

**Результат:**
```bash
docker compose up -d
curl http://localhost/health
# {"cpu": 12.3, "ram": 45.1, "disk": 5.0}
```

---

## Этап 3 — systemd

Автозапуск docker compose после перезагрузки сервера.

**Требования:**
- создать `toolkit.service` для systemd
- сервис запускает `docker compose up`
- сервис стартует автоматически при загрузке системы
- логи доступны через `journalctl`

**Результат:**
```bash
sudo systemctl enable toolkit
sudo systemctl start toolkit
sudo systemctl status toolkit
journalctl -u toolkit -f
```

---

## Этап 4 — GitHub Actions CI/CD

Автоматизировать проверку и сборку образа при push.

**Требования:**
- линтер — `flake8` или `ruff` на каждый push
- сборка Docker образа на каждый push в `main`
- пуш образа в Docker Hub при создании тега (`v*`)
- секреты (`DOCKER_USERNAME`, `DOCKER_PASSWORD`) через GitHub Secrets

**Пайплайн:**
```
push → lint → build → (если тег) → push to Docker Hub
```

**Файл:** `.github/workflows/ci.yml`

---

## Этап 5 — Kubernetes

Задеплоить toolkit в Kubernetes кластер.

**Требования:**
- `Deployment` — минимум 1 реплика
- `Service` — тип `ClusterIP`
- `Ingress` — маршрутизация по хосту
- все манифесты в папке `k8s/`

**Файлы:**
```
k8s/
├── deployment.yaml
├── service.yaml
└── ingress.yaml
```

**Результат:**
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl logs <pod>
```

---

## Структура репозитория (итог)

```
toolkit/
├── .github/
│   └── workflows/
│       └── ci.yml
├── commands/
│   ├── __init__.py
│   ├── scan.py
│   ├── backup.py
│   ├── monitor.py
│   └── deploy.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── nginx/
│   └── nginx.conf
├── toolkit.py
├── Dockerfile
├── docker-compose.yml
├── toolkit.service
├── requirements.txt
└── README.md
```

---

## README должен содержать

- описание проекта
- badges: CI статус, Docker Hub, Python версия
- быстрый старт (docker run)
- описание всех команд с примерами
- архитектурная схема (опционально)