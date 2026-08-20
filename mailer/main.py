import sys
import json
import os
import logging
import asyncio
import functools
from dotenv import load_dotenv

# En Windows, la consola por defecto usa cp1252, que no soporta los emojis (✅❌⚠)
# usados en los logs de este servicio y de sus repositorios. Forzamos UTF-8 para
# evitar UnicodeEncodeError al correr el servicio fuera de Docker (donde sí es UTF-8).
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from app.shared.infrastructure.messaging import RabbitMQTopicConsumer
from app.users.infrastructure.repositories import UserRepository
from app.users.domain.models import User
from app.notifications.infrastructure.repositories import NotificationRepository
from app.notifications.domain.models import ForecastCompletedEvent, ForecastFailedEvent, Recipient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [MAILER] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def _load_excluded_emails() -> set[str]:
    """Direcciones que nunca deben recibir notificaciones, aunque sean admin/empleado
    o estén ligadas al contrato (p. ej. buzones genéricos como info@...)."""
    raw = os.getenv("MAILER_EXCLUDE_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


EXCLUDED_EMAILS = _load_excluded_emails()


def _dedupe_recipients(*groups: list[Recipient], exclude_id: int) -> list[Recipient]:
    """Combina varias listas de destinatarios, quitando duplicados, la propia cuenta de
    servicio del mailer y las direcciones en MAILER_EXCLUDE_EMAILS."""
    seen: set[int] = set()
    result: list[Recipient] = []
    for group in groups:
        for r in group:
            if r.id == exclude_id or r.id in seen or r.email.lower() in EXCLUDED_EMAILS:
                continue
            seen.add(r.id)
            result.append(r)
    return result


async def handle_completed(message: dict, repo: NotificationRepository, requester: User):
    event = ForecastCompletedEvent.from_message(message)

    contract_users: list[Recipient] = []
    if event.contract_id is not None:
        contract_users = await repo.get_contract_users(event.contract_id, requester)
    else:
        logging.warning(
            f"Sistema {event.forecast_system_id} no tiene contrato asociado; solo se notificará a admins/empleados."
        )

    admins = await repo.get_admin_users(requester)
    recipients = _dedupe_recipients(contract_users, admins, exclude_id=requester.id)

    if not recipients:
        logging.warning(
            f"No hay destinatarios (ni usuarios del contrato {event.contract_id} ni admins/empleados); no se envía email."
        )
        return

    await repo.send_completed_email(recipients, event, requester)
    logging.info(f"Email de éxito procesado para ForecastSystem ID: {event.forecast_system_id}")


async def handle_failed(message: dict, repo: NotificationRepository, requester: User):
    event = ForecastFailedEvent.from_message(message)

    admins = await repo.get_admin_users(requester)
    recipients = _dedupe_recipients(admins, exclude_id=requester.id)

    if not recipients:
        logging.warning("No hay usuarios admin/empleados a los que notificar el fallo.")
        return

    await repo.send_failed_email(recipients, event)
    logging.info(f"Email de fallo procesado para ForecastSystem ID: {event.forecast_system_id}")


def process_message_callback(body: bytes, repo: NotificationRepository, requester: User):
    """Callback síncrono llamado por Pika; despacha a la lógica asíncrona según el tipo de evento."""
    try:
        message = json.loads(body.decode())
        event_type = message.get("event")

        logging.info(f"Recibido evento: {event_type} (forecast_system_id={message.get('forecast_system_id')})")

        if event_type == "forecast_system_completed":
            asyncio.run(handle_completed(message, repo, requester))
        elif event_type == "forecast_system_failed":
            asyncio.run(handle_failed(message, repo, requester))
        else:
            logging.warning(f"Evento desconocido, ignorado: {event_type}")

    except json.JSONDecodeError:
        logging.error(f"Error: No se pudo decodificar el mensaje JSON: {body}")
    except Exception as e:
        logging.error(f"Error inesperado en el callback: {e}", exc_info=True)


async def perform_initial_login() -> User:
    """Realiza el login inicial para obtener credenciales válidas (cuenta dedicada del mailer)."""
    api_user = os.getenv("MAILER_API_USER")
    api_password = os.getenv("MAILER_API_PASSWORD")

    if not api_user or not api_password:
        raise ValueError("MAILER_API_USER y MAILER_API_PASSWORD deben estar definidos en las variables de entorno.")

    logging.info(f"Iniciando sesión en la API como user='{api_user}'...")
    user_repo = UserRepository()
    user_session = await user_repo.login(api_user, api_password)
    logging.info(f"Login exitoso. Token obtenido para usuario ID: {user_session.id}")
    return user_session


def main():
    load_dotenv()

    try:
        user_session = asyncio.run(perform_initial_login())
    except Exception as e:
        logging.critical(f"No se pudo iniciar el mailer debido a fallo en login: {e}")
        return

    notification_repo = NotificationRepository()

    exchange_name = 'forecast_events_exchange'
    binding_key = os.getenv("BINDING_KEY", "forecast.#")

    callback_with_deps = functools.partial(
        process_message_callback,
        repo=notification_repo,
        requester=user_session
    )

    consumer = RabbitMQTopicConsumer(exchange_name, binding_key)

    logging.info(f"Mailer inicializado y autenticado. Esperando eventos en '{binding_key}'...")
    consumer.start_consuming(on_message_callback=callback_with_deps)


if __name__ == '__main__':
    main()
