# dockerfile for toolkit

FROM python:3.12 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

ARG APP_VERSION=1.0.0
LABEL version="${APP_VERSION}"

WORKDIR /app

COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PORT=5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

RUN useradd -r -s /bin/false appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 5000
CMD ["python", "toolkit.py", "serve"]