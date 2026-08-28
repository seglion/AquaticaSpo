import asyncio
import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.user.domain.model import User
from app.forecast_systems.application.services import ForecastService
from app.forecast_systems.domain.models import ForecastSystem
from app.shared.infrastructure.messaging import RabbitMQTopicPublisher


class ForecastRepository(ForecastService):
    """Implementación del repositorio para obtener sistemas de pronóstico desde la API."""

    async def get_forecast_systems(self, requester: User) -> List[ForecastSystem]:
        # 1. Comprobación de permisos
        if not requester.is_admin:
            raise PermissionError("Se requieren permisos de administrador para acceder a los sistemas de pronóstico.")

        # 2. Si el usuario es admin, proceder con la llamada a la API
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        headers = {"Authorization": f"Bearer {requester.session_USER}"}

        async with httpx.AsyncClient(base_url=backend_url, headers=headers) as client:
            try:
                response = await client.get("/forecast-systems/") # Asumiendo que este es el endpoint
                response.raise_for_status()
                
                # Mapeo manual para desacoplar el modelo del cron del modelo completo de la API.
                # Esto evita errores si la API añade nuevos campos que el cron no necesita.
                systems_data = response.json()
                return [
                    ForecastSystem(
                        id=data.get("id"),
                        hindcast_point_id=data.get("hindcast_point_id")
                    ) for data in systems_data
                ]
            except httpx.HTTPStatusError as e:
                print(f"Error al obtener los sistemas de pronóstico: {e.response.text}")
                raise

    async def download_data_forecast_systems(self, forecast_systems: List[ForecastSystem], requester: User) -> None:
        # 1. Comprobación de permisos (importante también aquí)
        if not requester.is_admin:
            raise PermissionError("Se requieren permisos de administrador para iniciar la descarga de datos.")
        # 2. Si el usuario es admin, proceder con la descarga y guardado de datos.
        
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        headers = {"Authorization": f"Bearer {requester.session_USER}"}
        
        # Creamos los clientes una sola vez fuera del bucle para mayor eficiencia
        async with httpx.AsyncClient(base_url=backend_url, headers=headers) as backend_client, \
             httpx.AsyncClient() as external_client:

            # Usamos el publisher como un context manager para asegurar que la conexión se abre
            # una sola vez y se cierra correctamente al final.
            with RabbitMQTopicPublisher(exchange_name='forecast_tasks_exchange') as publisher:
                for system in forecast_systems:
                    try:
                        # Obtener detalles del punto de pronóstico desde nuestro backend
                        response = await backend_client.get(f"/hindcast-points/{system.hindcast_point_id}")
                        
                        response.raise_for_status()
                        hindcast_point = response.json()
                        
                        # Descargar datos marinos de la API externa
                        marine_data = await self.fetch_marine_data(external_client, hindcast_point)
                        
                        if not marine_data:
                            print(f"\nNo se obtuvieron datos marinos para el punto {hindcast_point.get('id')}, continuando con el siguiente.")
                            continue

                        print(f"\nDatos marinos obtenidos para el punto {hindcast_point.get('id')}")

                        merged_data = marine_data

                        # Descargar datos de viento si el punto tiene wind_url configurado
                        wind_data = await self.fetch_wind_data(external_client, hindcast_point)
                        if wind_data:
                            print(f"Datos de viento obtenidos para el punto {hindcast_point.get('id')}")
                            # Merge del hourly de viento en los datos marinos
                            marine_hourly = marine_data.get("hourly", {})
                            wind_hourly = wind_data.get("hourly", {})

                            # Combinar hourly_units
                            marine_units = marine_data.get("hourly_units", {})
                            wind_units = wind_data.get("hourly_units", {})
                            marine_units.update(wind_units)

                            # Combinar hourly (se salta 'time' para no duplicarlo)
                            for key, values in wind_hourly.items():
                                if key != "time":
                                    marine_hourly[key] = values

                            merged_data = marine_data
                        else:
                            print(f"No se obtuvieron datos de viento para el punto {hindcast_point.get('id')}")

                        # Preparar el payload para enviar a nuestro backend
                        request_content = {
                            "point_id": hindcast_point.get('id'),
                            "downloaded_at": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
                            "data": merged_data
                        }

                        # Enviar los datos descargados a nuestro backend para guardarlos
                        post_response = await backend_client.post('/downloaded-data/', json=request_content)
                        
                        post_response.raise_for_status()
                        print(f"Datos guardados para el punto {hindcast_point.get('id')}")

                        # 4. Notificar al worker con los detalles precisos para la ejecución
                        downloaded_data_info = post_response.json()
                        downloaded_data_id = downloaded_data_info.get("id")

                        if downloaded_data_id:
                            message = {
                                "forecast_system_id": system.id,
                                "downloaded_data_id": downloaded_data_id
                            }
                            # La routing key describe el trabajo
                            routing_key = f"forecast.system.{system.id}"
                            publisher.send_message(routing_key, message)
                        else:
                            print(f"ADVERTENCIA: El backend no devolvió un ID para los datos del punto {hindcast_point.get('id')}. No se puede notificar al worker.")

                    except httpx.HTTPStatusError as e:
                        print(f"\nError de API al procesar el sistema {system.id}: {e.response.status_code} - {e.response.text}")
                        # Decidimos continuar con el siguiente sistema en caso de error en uno
                        continue
                    except Exception as e:
                        print(f"\nError inesperado al procesar el sistema {system.id}: {e}")
                        continue

    
    def normalize_model_name(self,model_name):
        return model_name.lower().replace('-', '_').replace(' ', '_')

    async def _get_with_retry(
        self, client: httpx.AsyncClient, url: str, params: Dict[str, Any],
        retries: int = 3, backoff_seconds: float = 3.0
    ) -> httpx.Response:
        """GET con reintentos ante fallos transitorios (5xx, errores de conexión).

        Open-Meteo devuelve 503 "The service is overloaded" de forma intermitente
        en horas punta; sin reintento, esas franjas se quedan sin datos de viento.
        """
        last_exception: Exception = RuntimeError("Sin intentos realizados")
        for attempt in range(1, retries + 1):
            try:
                response = await client.get(url, params=params)
                if response.status_code >= 500:
                    response.raise_for_status()
                return response
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                if attempt < retries:
                    print(f"Intento {attempt}/{retries} fallido para {url}: {e}. Reintentando en {backoff_seconds}s...")
                    await asyncio.sleep(backoff_seconds)
        raise last_exception

    async def fetch_marine_data(self, client: httpx.AsyncClient, point: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene datos de la API de Open-Meteo para un punto específico."""
        required_keys = ['id', 'url', 'latitude', 'longitude', 'models']
        if not all(key in point and point[key] is not None for key in required_keys):
            print(f"Ignorando punto por datos incompletos: {point.get('id', 'ID no disponible')}")
            return None

        point_id = point['id']
        url = point['url']

        if not url.startswith('https://marine-api.open-meteo.com/v1/marine'):
            print(f"Ignorando punto id={point_id}. URL inválida: {url}")
            return None

        params = {
            'latitude': point['latitude'],
            'longitude': point['longitude'],
            'hourly': 'wave_height,wave_direction,wave_period',
            'models': ','.join(self.normalize_model_name(m) for m in point['models'])
        }

        try:
            response = await self._get_with_retry(client, url, params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error de estado HTTP para punto id={point_id}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error de conexión al consultar API para punto id={point_id}: {e}")
            return None

    async def fetch_wind_data(self, client: httpx.AsyncClient, point: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene datos de viento de la API de Open-Meteo para un punto específico."""
        wind_url = point.get("wind_url")
        if not wind_url:
            return None

        wind_models = point.get("wind_models")
        params = {
            'latitude': point['latitude'],
            'longitude': point['longitude'],
            'hourly': 'wind_speed_10m,wind_gusts_10m,wind_direction_10m',
        }
        if wind_models:
            params['models'] = ','.join(self.normalize_model_name(m) for m in wind_models)

        try:
            response = await self._get_with_retry(client, wind_url, params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error de estado HTTP al obtener viento para punto id={point.get('id')}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error de conexión al consultar API de viento para punto id={point.get('id')}: {e}")
            return None


# --- Bloque de prueba ---
async def main_test():
    # Cargar variables de entorno desde .env para facilitar las pruebas locales
    # Esto es especialmente útil para que RABBITMQ_HOST se establezca en 'localhost'
    from dotenv import load_dotenv
    load_dotenv()

    os.system('cls' if os.name == 'nt' else 'clear')
    """Función principal para probar el ForecastRepository."""
    print("--- Iniciando prueba de ForecastRepository ---")

    # Paso 1: Iniciar sesión para obtener un objeto User con token y rol.
    # Reutilizamos la lógica de infraestructura del usuario.
    from app.user.infrastructure.infrastructure import UserRepository

    test_user = os.getenv("API_USER")
    test_password = os.getenv("API_PASSWORD")

    if not test_user or not test_password:
        print("\nERROR: Por favor, define las variables de entorno API_USER y API_PASSWORD.")
        return

    try:
        print(f"Intentando iniciar sesión como '{test_user}' para obtener la sesión...")
        user_repo = UserRepository()
        user_session = await user_repo.login(test_user, test_password)
        print(f"✅ Login exitoso. El usuario es admin: {user_session.is_admin}")
    except Exception as e:
        print(f"\n❌ Falló el login inicial: {e}")
        return

    # Paso 2 y 3: Obtener sistemas y luego descargar sus datos.
    print("\nIntentando obtener y descargar datos de los sistemas de pronóstico...")
    forecast_repo = ForecastRepository()
    try:
        systems = await forecast_repo.get_forecast_systems(user_session)
        if not systems:
            print("\n✅ No se encontraron sistemas de pronóstico para procesar.")
            return

        print(f"\n✅ ¡Éxito! {len(systems)} sistema(s) de pronóstico obtenido(s):")
        for system in systems:
            print(f"  - {system}")

        print("\nIniciando proceso de descarga de datos...")
        await forecast_repo.download_data_forecast_systems(systems, user_session)
        print("\n✅ ¡Proceso de descarga completado!")

    except PermissionError as e:
        print(f"\n✅ ¡Prueba exitosa! Se denegó el acceso como se esperaba: {e}")
    except Exception as e:
        print(f"\n❌ Falló la prueba con un error inesperado: {e}")



if __name__ == "__main__":
    import asyncio
    # Para ejecutar, asegúrate de que el backend esté corriendo y
    # hayas exportado las variables API_USER y API_PASSWORD.
    # Prueba con un usuario admin y otro no-admin para ver ambos resultados.
    asyncio.run(main_test())