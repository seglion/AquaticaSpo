# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instalar el demonio cron y netcat (necesario para wait-for-it.sh)
RUN apt-get update && apt-get -y install cron netcat-openbsd

# Copiar el script de espera y darle permisos de ejecución
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copiar el archivo crontab al directorio de cron
COPY crontab /etc/cron.d/app-cron

# Dar permisos de ejecución al archivo crontab
RUN chmod 0644 /etc/cron.d/app-cron

# Copiar el script de entrada y darle permisos de ejecución
COPY entrypoint.sh /app/entrypoint.sh
# Corregir posibles finales de línea de Windows (CRLF) y dar permisos de ejecución
RUN sed -i 's/\r$//g' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Copiar el resto del código de la aplicación
COPY . .

# Usar el script de entrada como comando de inicio
CMD ["/app/entrypoint.sh"]
