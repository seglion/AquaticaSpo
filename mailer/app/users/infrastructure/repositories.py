from app.users.domain.models import User
from app.users.application.services import UserService
import httpx
import os


class UserRepository(UserService):
    async def login(self, user, password):
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")

        async with httpx.AsyncClient(base_url=backend_url) as client:
            login_data = {"username": user, "password": password}
            try:
                login_resp = await client.post("/users/login", data=login_data)
                login_resp.raise_for_status()
                token_data = login_resp.json()

                return User(
                    id=token_data["user_id"],
                    session_USER=token_data["access_token"],
                    is_admin=token_data["is_admin"]
                )
            except httpx.HTTPStatusError as e:
                print(f"Error de autenticación: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                print(f"No se pudo conectar al servicio de backend en {backend_url}: {e}")
                raise
