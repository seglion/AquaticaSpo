from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.auth.jwt_service import JWTService
from app.shared.config import settings
from app.users.infrastructure.infrastructure import UserRepository
from app.shared.dependencies import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
jwt_service = JWTService(secret_key=settings.JWT_SECRET_KEY)

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_session)):
    try:
        payload = jwt_service.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    repo = UserRepository(session)
    user = await repo.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user