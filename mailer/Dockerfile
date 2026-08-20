FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# (contexto de build = raíz del repo, ver docker-compose.yml)
COPY mailer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mailer/ .

# Umbrales de alerta compartidos con el frontend y forecastWorker (única fuente de verdad)
COPY alert_thresholds.json .

CMD ["python", "main.py"]
