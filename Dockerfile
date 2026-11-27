FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias del sistema necesarias para compilación o PostgreSQL si aplican
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias primero para aprovechar caché de Docker
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Crear usuario sin privilegios para mayor seguridad en contenedores y Kuberus
RUN useradd --create-home --shell /bin/bash appuser

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]