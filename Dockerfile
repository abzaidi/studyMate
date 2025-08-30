# ---------- base image ----------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/usr/local/bin:$PATH"

# System deps (poppler-utils for PDF processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------- builder to cache deps ----------
FROM base AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ---------- final runtime ----------
FROM base
WORKDIR /app

# Install deps from prebuilt wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy project code (includes studymate/ with manage.py inside)
COPY . .

# Django settings
ENV DJANGO_SETTINGS_MODULE=studymate.settings

# Expose for local use (Cloud Run ignores EXPOSE)
EXPOSE 8080

# Create non-root user
RUN useradd -m appuser
USER appuser

# Entrypoint: run migrations, collectstatic, and start Gunicorn
ENTRYPOINT ["bash", "-lc", "cd studymate && python manage.py migrate --noinput && python manage.py collectstatic --noinput || true; exec gunicorn studymate.wsgi:application --chdir studymate --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 0"]
