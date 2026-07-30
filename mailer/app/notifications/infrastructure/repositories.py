import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageDraw

from app.users.domain.models import User
from app.notifications.domain.models import (
    Recipient,
    ForecastCompletedEvent,
    ForecastFailedEvent,
    ZoneAlert,
)
from app.notifications.application.services import NotificationService

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

MADRID_TZ = ZoneInfo("Europe/Madrid")
UTC_TZ = ZoneInfo("UTC")


def madrid_time(value: str, fmt: str = "%d/%m/%Y %H:%M") -> str:
    """Filtro Jinja2: convierte un timestamp (UTC, con o sin sufijo de zona) a
    hora local de Madrid. Todos los timestamps que genera el sistema
    (forecastWorker) son UTC; aquí solo se convierten para mostrarlos."""
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(MADRID_TZ).strftime(fmt)


_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "j2"]),
)
_jinja_env.filters["madrid_time"] = madrid_time

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"

# Ortofotos PNOA del IGN (Instituto Geográfico Nacional), servicio público sin
# necesidad de API key.
IGN_WMS_URL = "https://www.ign.es/wms-inspire/pnoa-ma"
MAP_BBOX_DELTA_DEGREES = 0.004  # ~450 m de radio alrededor de la zona
MAP_WIDTH_PX = 600
MAP_HEIGHT_PX = 340
MAP_MARKER_COLOR = "#dc2626"
MAP_MARKER_RADIUS_PX = 9


class NotificationRepository(NotificationService):
    def __init__(self):
        self.backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        self.brevo_api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("BREVO_SENDER_EMAIL")
        self.sender_name = os.getenv("BREVO_SENDER_NAME", "AquaticaSpo")

    def _api_client(self, requester: User) -> httpx.AsyncClient:
        headers = {"Authorization": f"Bearer {requester.session_USER}"}
        return httpx.AsyncClient(base_url=self.backend_url, headers=headers)

    async def _relogin(self, requester: User) -> None:
        """Renueva el token de sesión (mutando 'requester' in-place) tras un 401.
        La cuenta de servicio del mailer vive indefinidamente, pero su JWT expira
        (ACCESS_TOKEN_EXPIRE_MINUTES); sin esto, un mailer de larga duración deja
        de poder llamar a la API pasado ese tiempo."""
        from app.users.infrastructure.repositories import UserRepository

        api_user = os.getenv("MAILER_API_USER")
        api_password = os.getenv("MAILER_API_PASSWORD")
        fresh = await UserRepository().login(api_user, api_password)
        requester.session_USER = fresh.session_USER
        requester.id = fresh.id
        requester.is_admin = fresh.is_admin
        print("🔄 Sesión del mailer renovada tras token expirado")

    async def _get_authed(self, path: str, requester: User) -> httpx.Response:
        """GET autenticado con un reintento automático si el token ha expirado (401)."""
        async with self._api_client(requester) as client:
            response = await client.get(path)
        if response.status_code == 401:
            await self._relogin(requester)
            async with self._api_client(requester) as client:
                response = await client.get(path)
        return response

    async def get_contract_users(self, contract_id: int, requester: User) -> List[Recipient]:
        try:
            response = await self._get_authed(f"/contracts/{contract_id}/users", requester)
            response.raise_for_status()
            return [Recipient(**u) for u in response.json()]
        except httpx.HTTPStatusError as e:
            print(f"Error obteniendo usuarios del contrato {contract_id}: {e.response.text}")
            return []

    async def get_admin_users(self, requester: User) -> List[Recipient]:
        try:
            response = await self._get_authed("/users/", requester)
            response.raise_for_status()
            all_users = [Recipient(**u) for u in response.json()]
            return [u for u in all_users if u.is_admin or u.is_employee]
        except httpx.HTTPStatusError as e:
            print(f"Error obteniendo usuarios administradores: {e.response.text}")
            return []

    async def _fetch_zone_map_attachment(self, zone: ZoneAlert) -> Optional[Dict[str, str]]:
        """Descarga una ortofoto PNOA del IGN centrada en la zona y le dibuja un
        marcador. Devuelve un adjunto listo para Brevo (name/content en base64),
        o None si la zona no tiene coordenadas o falla la descarga (nunca debe
        impedir el envío del email por esto)."""
        if zone.lat is None or zone.lon is None:
            return None

        bbox = (
            f"{zone.lon - MAP_BBOX_DELTA_DEGREES},{zone.lat - MAP_BBOX_DELTA_DEGREES},"
            f"{zone.lon + MAP_BBOX_DELTA_DEGREES},{zone.lat + MAP_BBOX_DELTA_DEGREES}"
        )
        params = {
            "SERVICE": "WMS",
            "VERSION": "1.1.1",
            "REQUEST": "GetMap",
            "LAYERS": "OI.OrthoimageCoverage",
            "STYLES": "",
            "SRS": "EPSG:4326",
            "BBOX": bbox,
            "WIDTH": MAP_WIDTH_PX,
            "HEIGHT": MAP_HEIGHT_PX,
            "FORMAT": "image/png",
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(IGN_WMS_URL, params=params)
                response.raise_for_status()

            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            draw = ImageDraw.Draw(image)
            cx, cy = image.width // 2, image.height // 2
            r = MAP_MARKER_RADIUS_PX
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAP_MARKER_COLOR, outline="#ffffff", width=2)

            buf = io.BytesIO()
            image.save(buf, format="PNG")
            content_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"name": f"zona_{zone.zone_id}_ortofoto.png", "content": content_b64}
        except Exception as e:
            print(f"⚠ No se pudo generar la ortofoto de la zona {zone.zone_id}: {e}")
            return None

    async def _send_via_brevo(
        self,
        recipient: Recipient,
        subject: str,
        html_body: str,
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        if not self.brevo_api_key or not self.sender_email:
            print(f"⚠ BREVO_API_KEY/BREVO_SENDER_EMAIL no configurados; no se envía email a {recipient.email}")
            return

        headers = {
            "api-key": self.brevo_api_key,
            "content-type": "application/json",
            "accept": "application/json",
        }
        payload = {
            "sender": {"name": self.sender_name, "email": self.sender_email},
            "to": [{"email": recipient.email, "name": recipient.username}],
            "subject": subject,
            "htmlContent": html_body,
        }
        if attachments:
            payload["attachment"] = attachments
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(BREVO_SEND_URL, headers=headers, json=payload)
                response.raise_for_status()
                print(f"✅ Email enviado a {recipient.email} (Brevo messageId: {response.json().get('messageId')})")
            except httpx.HTTPStatusError as e:
                print(f"❌ Error enviando email a {recipient.email}: {e.response.text}")

    async def send_completed_email(self, recipients: List[Recipient], event: ForecastCompletedEvent) -> None:
        if not recipients:
            print(f"No hay destinatarios para el sistema {event.forecast_system_id}, no se envía email.")
            return

        zones = event.zones_by_severity()

        # Se generan las ortofotos una sola vez (no una vez por destinatario) y se
        # reutilizan como adjuntos inline (referenciados por 'cid:' en el HTML).
        attachments: List[Dict[str, str]] = []
        zone_map_cids: Dict[int, str] = {}
        for zone in zones:
            attachment = await self._fetch_zone_map_attachment(zone)
            if attachment:
                attachments.append(attachment)
                zone_map_cids[zone.zone_id] = attachment["name"]

        template = _jinja_env.get_template("forecast_completed.html.j2")
        html_body = template.render(
            forecast_system_id=event.forecast_system_id,
            forecast_system_name=event.forecast_system_name,
            executed_at=event.executed_at,
            zones=zones,
            zone_map_cids=zone_map_cids,
            wind_alert=event.wind_alert,
        )
        subject = f"[AquaticaSpo] Previsión ejecutada – {event.forecast_system_name or event.forecast_system_id}"

        for recipient in recipients:
            await self._send_via_brevo(recipient, subject, html_body, attachments=attachments)

    async def send_failed_email(self, recipients: List[Recipient], event: ForecastFailedEvent) -> None:
        if not recipients:
            print(f"No hay administradores a los que notificar el fallo del sistema {event.forecast_system_id}.")
            return

        template = _jinja_env.get_template("forecast_failed.html.j2")
        html_body = template.render(
            forecast_system_id=event.forecast_system_id,
            forecast_system_name=event.forecast_system_name,
            failed_at=event.failed_at,
            error_message=event.error_message,
        )
        subject = f"[AquaticaSpo] ERROR en previsión – {event.forecast_system_name or event.forecast_system_id}"

        for recipient in recipients:
            await self._send_via_brevo(recipient, subject, html_body)
