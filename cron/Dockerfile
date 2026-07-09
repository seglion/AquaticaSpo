# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instalar el demonio cron, netcat (para wait-for-it.sh), procps (para el comando 'ps')
# y tzdata, y limpiar el caché de apt.
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron netcat-openbsd procps tzdata && \
    rm -rf /var/lib/apt/lists/*

# Fijar la zona horaria del sistema a Europe/Madrid: cron usa la hora local del
# sistema (no respeta una variable TZ= dentro del propio crontab en esta
# versión), así que el schedule del crontab (7:00/19:00) solo sale correcto en
# hora de Madrid si el reloj del contenedor está en esa zona. tzdata gestiona
# el cambio CET/CEST automáticamente.
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiar el script de espera y darle permisos de ejecución
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copiar el archivo crontab al directorio de cron
COPY crontab /etc/cron.d/app-cron

# Copiar el script de entrada y darle permisos de ejecución
COPY entrypoint.sh /app/entrypoint.sh

# Corregir finales de línea (para compatibilidad con Windows) y establecer permisos
RUN sed -i 's/\r$//g' /etc/cron.d/app-cron /app/entrypoint.sh && \
    chmod 0644 /etc/cron.d/app-cron && \
    chmod +x /app/entrypoint.sh

# Copiar el resto del código de la aplicación
COPY . .

# Usar el script de entrada como comando de inicio
CMD ["/app/entrypoint.sh"]
