from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.shared.auth.jwt_service import JWTService
from app.shared.config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

jwt_service = JWTService(secret_key=JWT_SECRET_KEY)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt_service.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Aquí podrías recuperar el usuario de la base de datos si quieres
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")