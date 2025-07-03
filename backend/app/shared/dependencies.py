
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status # Importa HTTPException y status

from app.shared.database import async_session_factory

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db: AsyncSession = async_session_factory() # Renombramos para claridad
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback() # 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos: {e}"
        )
    finally:
        await db.close() 