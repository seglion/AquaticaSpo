import pytest_asyncio# pylint: disable=import-error
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.shared.config import settings

@pytest_asyncio.fixture  # function-scoped por defecto
async def engine():
    engine = create_async_engine(settings.database_url, echo=False)
    try:
        yield engine
    finally:
        # Cerramos el engine al acabar el test
        await engine.dispose()

@pytest_asyncio.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session