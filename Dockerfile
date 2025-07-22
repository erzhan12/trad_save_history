# Multi-stage Dockerfile for Bybit Data Collector
# Stage 1: Build stage
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN uv sync --locked 

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]
