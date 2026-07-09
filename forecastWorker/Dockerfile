# Usar una imagen base oficial de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Variables de entorno para evitar archivos .pyc y buffers en stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para scipy/numpy/pandas si es necesario
# netcat para wait-for-it (opcional)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
# (contexto de build = raíz del repo, ver docker-compose.yml)
COPY forecastWorker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY forecastWorker/ .

# Umbrales de alerta compartidos con el frontend (única fuente de verdad)
COPY alert_thresholds.json .

# Parámetros de remonte (wave runup) por zona, usados en la propagación.
COPY remonte_params.json .

# Comando por defecto para iniciar el worker
CMD ["python", "main.py"]
