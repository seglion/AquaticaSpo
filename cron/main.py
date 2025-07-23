import asyncio
import os
import time
from dotenv import load_dotenv

# Importar las implementaciones de infraestructura que contienen la lógica
from app.user.infrastructure.infrastructure import UserRepository
from app.forecast_systems.infrastructure.repositories import ForecastRepository


async def run_job():
    """
    Ejecuta un único ciclo del trabajo del cron:
    1. Inicia sesión.
    2. Obtiene los sistemas de pronóstico.
    3. Descarga los datos y notifica a los workers.
    """
    print("--- [CRON] Iniciando nuevo ciclo de trabajo ---")

    # Paso 1: Iniciar sesión para obtener un objeto User con token y rol.
    user_repo = UserRepository()
    api_user = os.getenv("API_USER")
    api_password = os.getenv("API_PASSWORD")

    if not api_user or not api_password:
        print("[CRON] ERROR: Las variables de entorno API_USER y API_PASSWORD no están definidas.")
        return

    try:
        print(f"[CRON] Intentando iniciar sesión como '{api_user}'...")
        user_session = await user_repo.login(api_user, api_password)
        print(f"[CRON] Login exitoso. El usuario es admin: {user_session.is_admin}")
    except Exception as e:
        print(f"[CRON] ❌ Falló el login. Abortando ciclo: {e}")
        return

    # Paso 2 y 3: Obtener sistemas y luego descargar sus datos.
    print("[CRON] Intentando obtener y descargar datos de los sistemas de pronóstico...")
    forecast_repo = ForecastRepository()
    try:
        systems = await forecast_repo.get_forecast_systems(user_session)
        if not systems:
            print("[CRON] No se encontraron sistemas de pronóstico para procesar.")
            return

        print(f"[CRON] ✅ {len(systems)} sistema(s) de pronóstico obtenido(s).")

        print("[CRON] Iniciando proceso de descarga de datos y notificación...")
        await forecast_repo.download_data_forecast_systems(systems, user_session)
        print("[CRON] ✅ ¡Proceso de descarga y notificación completado!")

    except PermissionError as e:
        print(f"[CRON] ❌ Error de permisos. Abortando ciclo: {e}")
    except Exception as e:
        print(f"[CRON] ❌ Falló el ciclo de trabajo con un error inesperado: {e}")


if __name__ == "__main__":
    """
    Punto de entrada del script.
    Carga las variables de entorno y ejecuta el trabajo una sola vez.
    El demonio 'cron' del sistema se encargará de llamar a este script periódicamente.
    """
    load_dotenv()
    asyncio.run(run_job())