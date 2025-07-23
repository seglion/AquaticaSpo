#!/bin/sh
# entrypoint.sh

# Salir inmediatamente si un comando falla.
set -e

# Guarda todas las variables de entorno actuales en un archivo que cron pueda usar.
echo "--- [CRON_ENTRYPOINT] Guardando variables de entorno para cron... ---"
printenv | sed 's/^\(.*\)$/export \1/g' > /etc/environment

# Esperar a que el servicio de API esté listo antes de continuar.
echo "--- [CRON_ENTRYPOINT] Esperando a que el servicio API esté disponible en api:8000... ---"
/usr/local/bin/wait-for-it.sh api:8000 --timeout=60

# Esperar a que el servicio de RabbitMQ esté listo antes de continuar.
echo "--- [CRON_ENTRYPOINT] Esperando a que el servicio RabbitMQ esté disponible en rabbitmq:5672... ---"
/usr/local/bin/wait-for-it.sh rabbitmq:5672 --timeout=60

# Ejecuta el trabajo inmediatamente al iniciar el contenedor.
echo "--- [CRON_ENTRYPOINT] Ejecutando el trabajo por primera vez al iniciar... ---"
python main.py

# Inicia el demonio cron en primer plano para que se encargue de las ejecuciones programadas.
echo "--- [CRON_ENTRYPOINT] Iniciando el demonio cron para ejecuciones programadas... ---"
exec cron -f