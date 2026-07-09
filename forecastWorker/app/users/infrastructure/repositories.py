from app.users.domain.models import User
from app.users.application.services import UserService
import httpx
import os

class UserRepository(UserService):
    async def login(self, user, password):
        # 1. Obtener la URL del backend desde una variable de entorno.
        #    El valor por defecto "http://localhost:8001" se usará si la variable no está definida.
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")

        async with httpx.AsyncClient(base_url=backend_url) as client:
            login_data = {"username": user, "password": password}
            
            # 2. Realizar la petición POST al endpoint de login del backend.
            #    Asumo que tienes un endpoint como /token que espera un form-data.
            try:
                login_resp = await client.post("/users/login", data=login_data)
                login_resp.raise_for_status()
                
                # 3. Procesar la respuesta y crear el objeto de dominio User.
                #    Asumo que el backend devuelve un JSON con 'access_token'.
                token_data = login_resp.json()

                return User(
                    id=token_data["user_id"],
                    session_USER=token_data["access_token"],
                    is_admin=token_data["is_admin"]
                )

            except httpx.HTTPStatusError as e:
                # Aquí puedes manejar errores específicos, como credenciales inválidas.
                print(f"Error de autenticación: {e.response.status_code} - {e.response.text}")
                raise  # O manejarlo de forma más elegante
            except httpx.RequestError as e:
                # Manejar errores de conexión (ej. el backend no está disponible)
                print(f"No se pudo conectar al servicio de backend en {backend_url}: {e}")
                raise
            








# --- Bloque de prueba ---
async def main_test():
    """Función principal para probar el login."""
    # Cargar variables de entorno desde .env para facilitar las pruebas locales
    # Esto es especialmente útil para que BACKEND_API_URL se establezca en 'localhost'
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Iniciando prueba de login ---")

    # Leemos las credenciales desde variables de entorno para no hardcodearlas
    test_user = os.getenv("API_USER")
    test_password = os.getenv("API_PASSWORD")

    if not test_user or not test_password:
        print("\nERROR: Por favor, define las variables de entorno API_USER y API_PASSWORD.")
        return

    repo = UserRepository()
    try:
        print(f"Intentando iniciar sesión como '{test_user}'...")
        user_session = await repo.login(test_user, test_password)
        print("\n✅ ¡Login exitoso!")
        print(f"Objeto User recibido: {user_session}")
    except Exception as e:
        print(f"\n❌ Falló el test de login: {e}")


if __name__ == "__main__":
    import asyncio
    # Para ejecutar esta prueba, asegúrate de que el backend esté corriendo y
    # que tu archivo .env tenga API_USER y API_PASSWORD.
    # Ejecuta desde la raíz del proyecto con:
    # python -m forecastWorker.app.users.infrastructure.repositories
    asyncio.run(main_test())