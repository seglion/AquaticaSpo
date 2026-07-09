import sys
import json
import os
import time
import logging
import asyncio
import functools
from datetime import datetime, timezone
from dotenv import load_dotenv

# En Windows, la consola por defecto usa cp1252, que no soporta los emojis (✅❌⚠✔🔄)
# usados en los logs de este servicio y de sus repositorios. Forzamos UTF-8 para
# evitar UnicodeEncodeError al correr el servicio fuera de Docker (donde sí es UTF-8).
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from app.shared.infrastructure.messaging import RabbitMQTopicConsumer, RabbitMQTopicPublisher
from app.users.infrastructure.repositories import UserRepository
from app.forecastSystem.infrastructure.repositories import ForecastWorkerRepository
from app.users.domain.models import User

FORECAST_EVENTS_EXCHANGE = 'forecast_events_exchange'


def _publish_forecast_event(routing_key: str, payload: dict):
    """Publica un evento de finalización del worker. Nunca debe interrumpir
    el flujo principal: cualquier fallo al publicar solo se loguea."""
    try:
        with RabbitMQTopicPublisher(exchange_name=FORECAST_EVENTS_EXCHANGE) as publisher:
            publisher.send_message(routing_key, payload)
    except Exception as e:
        logging.error(f"⚠ No se pudo publicar el evento '{routing_key}': {e}", exc_info=True)

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [WORKER] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def process_async_task(forecast_id: int, data_id: int, repo: ForecastWorkerRepository, requester: User):
    """
    Lógica de negocio asíncrona que orquesta todo el proceso de cálculo.
    """
    system = None
    try:
        logging.info(f"--- [START] Procesando tarea para ForecastSystem ID: {forecast_id} ---")

        # 1. Obtener configuración del Sistema de Previsión
        logging.info(f"1. Obteniendo configuración del sistema (ID: {forecast_id})...")
        system = await repo.get_forecast_system(forecast_id, requester)
        logging.info(f"   ✔ Sistema obtenido: {system.name}")

        # 2. Obtener Zonas de Previsión
        logging.info(f"2. Obteniendo zonas de previsión asociadas...")
        zones = await repo.get_forecast_zones(forecast_id, requester)
        logging.info(f"   ✔ Zonas obtenidas: {len(zones)} zonas encontradas.")

        # 3. Obtener Datos de Hindcast (Descargados previamente)
        logging.info(f"3. Obteniendo datos de hindcast descargados (Data ID: {data_id})...")
        hindcast_data = await repo.get_hindcast_data(data_id, requester)
        logging.info(f"   ✔ Datos de hindcast obtenidos correctamente.")

        # 4. Calibración
        logging.info(f"4. Ejecutando calibración de datos...")
        # Nota: calibration_hindcast_data requiere el hindcast_point_id del sistema
        calibrated_data = await repo.calibration_hindcast_data(
            download_data=hindcast_data,
            hinccast_point_id=system.hindcast_point_id,
            requester=requester
        )
        if calibrated_data:
             logging.info(f"   ✔ Calibración completada para {len(calibrated_data)} modelos.")
        else:
             logging.warning(f"   ⚠ No se obtuvieron datos calibrados.")


        # 5. Crear Hipercubo (Parámetros de propagación)
        logging.info(f"5. Generando hipercubo de parámetros...")
        # Define los rangos del hipercubo (estos podrían venir de configuración en el futuro)
        hypercube = repo.create_hypercube(
            Hsig=[0.1, 1, 2, 3, 5, 7, 9, 11, 14],
            Tp=[5, 8, 10, 13, 16, 19, 25],
            Dir=[270, 292.5, 315, 337.5, 0, 22.5, 45, 67.5, 90],
            Nivel=[0, 4.5]
        )
        logging.info(f"   ✔ Hipercubo generado con {len(hypercube)} puntos.")

        # 6. Propagación
        logging.info(f"6. Ejecutando propagación (SWAN)...")
        propagation_results_json = repo.propagation(
            hindcast=calibrated_data,
            zones=zones,
            hypercube=hypercube
        )
        
        # 7. Guardar Resultados
        logging.info(f"7. Guardando resultados de propagación en la base de datos...")
        zone_alerts = await repo.save_forecast_results(
            system_id=forecast_id,
            zones=zones,
            propagation_results_json=propagation_results_json,
            requester=requester
        )
        logging.info(f"   ✔ Propagación completada y resultados guardados.")
        # Logging truncado para no saturar
        logging.info(f"   Resultados generados (primeros 200 chars): {propagation_results_json[:200]}...")

        logging.info(f"--- [END] Tarea finalizada exitosamente para ForecastSystem ID: {forecast_id} ---")

        success_payload = {
            "event": "forecast_system_completed",
            "forecast_system_id": forecast_id,
            "forecast_system_name": system.name,
            "contract_id": system.contract_id,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "zones": zone_alerts,
        }
        _publish_forecast_event(f"forecast.completed.{forecast_id}", success_payload)

    except Exception as e:
        logging.error(f"❌ Error durante el procesamiento asíncrono: {e}", exc_info=True)

        failure_payload = {
            "event": "forecast_system_failed",
            "forecast_system_id": forecast_id,
            "forecast_system_name": system.name if system else None,
            "contract_id": system.contract_id if system else None,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": str(e),
        }
        _publish_forecast_event(f"forecast.failed.{forecast_id}", failure_payload)

        # Aquí podrías relanzar la excepción si quieres que RabbitMQ reencole el mensaje (nack)
        raise

def process_message_callback(body: bytes, repo: ForecastWorkerRepository, requester: User):
    """
    Callback síncrono llamado por Pika.
    Actúa como puente (wrapper) para llamar a la lógica asíncrona.
    """
    try:
        message_data = json.loads(body.decode())
        forecast_id = message_data.get("forecast_system_id")
        data_id = message_data.get("downloaded_data_id")

        if not forecast_id or not data_id:
            logging.warning("Mensaje inválido recibido, faltan IDs: %s", message_data)
            return

        logging.info(f"Recibido mensaje: forecast_id={forecast_id}, data_id={data_id}")
        
        # Ejecutar la lógica asíncrona de forma síncrona (bloqueante para este hilo)
        asyncio.run(process_async_task(forecast_id, data_id, repo, requester))

    except json.JSONDecodeError:
        logging.error("Error: No se pudo decodificar el mensaje JSON: %s", body)
    except Exception as e:
        logging.error(f"Error inesperado en el callback: {e}", exc_info=True)


async def perform_initial_login() -> User:
    """Realiza el login inicial para obtener credenciales válidas."""
    api_user = os.getenv("API_USER")
    api_password = os.getenv("API_PASSWORD")
    
    if not api_user or not api_password:
        raise ValueError("API_USER y API_PASSWORD deben estar definidos en las variables de entorno.")

    logging.info(f"Iniciando sesión en la API como user='{api_user}'...")
    user_repo = UserRepository()
    user_session = await user_repo.login(api_user, api_password)
    logging.info(f"Login exitoso. Token obtenido para usuario ID: {user_session.id}")
    return user_session

def main():
    load_dotenv()
    
    # 1. Configuración inicial y Login
    try:
        # Necesitamos un loop para ejecutar el login asíncrono antes de entrar al loop de Pika
        user_session = asyncio.run(perform_initial_login())
    except Exception as e:
        logging.critical(f"No se pudo iniciar el worker debido a fallo en login: {e}")
        return

    # 2. Inicializar Repositorio
    worker_repo = ForecastWorkerRepository()

    # 3. Configurar RabbitMQ Consumer
    exchange_name = 'forecast_tasks_exchange'
    binding_key = os.getenv("BINDING_KEY", "forecast.system.1") # Se puede configurar por variable de entorno
    
    # Usamos functools.partial para inyectar las dependencias (repo y user_session) al callback
    callback_with_deps = functools.partial(
        process_message_callback, 
        repo=worker_repo, 
        requester=user_session
    )

    consumer = RabbitMQTopicConsumer(exchange_name, binding_key)
    
    logging.info(f"Worker inicializado y autenticado. Esperando tareas en '{binding_key}'...")
    consumer.start_consuming(on_message_callback=callback_with_deps)

if __name__ == '__main__':
    main()