# 🕒 AquaticaSpo Cron Service

> Orquestador de tareas programadas para la actualización de pronósticos.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Alpine-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Cron](https://img.shields.io/badge/Cron-Scheduler-orange?style=for-the-badge)

## 📖 Descripción

El servicio **Cron** es un componente autónomo encargado de desencadenar periódicamente el proceso de actualización de los sistemas de pronóstico. Se ejecuta en un contenedor independiente y utiliza el planificador `cron` de Linux para invocar scripts de mantenimiento y descarga.

## ⚙️ Funcionamiento

El servicio ejecuta un script principal (`main.py`) siguiendo una programación definida. Su flujo de trabajo es el siguiente:

1.  **Autenticación**: Se loguea contra la infraestructura del Backend utilizando credenciales de sistema (`API_USER` / `API_PASSWORD`).
2.  **Identificación de Tareas**: Consulta los sistemas de pronóstico activos (`ForecastSystem`) que requieren actualización.
3.  **Ejecución**:
    - Descarga metadatos preliminares.
    - Notifica a los Workers (a través de RabbitMQ o llamadas directas) para iniciar el procesamiento pesado.

## 📅 Programación (Schedule)

La programación se define en el archivo `crontab`.

| Frecuencia | Comando | Descripción |
|------------|---------|-------------|
| **Cada 30 min** | `python /app/main.py` | Ejecuta el ciclo de actualización de pronósticos. |

## 🚀 Instalación y Despliegue

Este servicio está diseñado para ejecutarse dentro de un contenedor **Docker**.

### Variables de Entorno Requeridas

Estas variables son críticas para que el Cron pueda autenticarse y operar corréctamente.

```ini
API_USER=sistema@aquaticaspo.com
API_PASSWORD=tu_password_seguro_de_sistema
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=aquaticaspo
```

### Ejecutar con Docker

Construye y levanta el servicio junto con el resto de la plataforma:

```bash
docker-compose up -d cron
```

## 🛠 Desarrollo Local

Si necesitas ejecutar el script manualmente para pruebas:

1.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configura las variables de entorno en un archivo `.env`.
3.  Ejecuta el script:
    ```bash
    python main.py
    ```

## 📂 Estructura

```
cron/
├── app/                  # Lógica del cron (Repositorios, Modelos importados)
├── crontab               # Archivo de configuración de cron
├── main.py               # Script de entrada (Entrypoint)
├── entrypoint.sh         # Script de inicio del contenedor
└── Dockerfile            # Definición de la imagen Docker
```

---
Desarrollado para **Miguel Angel Vigo Baz**.
