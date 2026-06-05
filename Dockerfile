FROM python:3.11-slim

RUN apt-get update && apt-get install -y python3-tk && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-dev.txt .
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r requirements-dev.txt

COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["/app/.venv/bin/python3", "main.py"]
