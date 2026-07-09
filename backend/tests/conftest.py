import pytest_asyncio# pylint: disable=import-error
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.shared.config import settings
# Import relevant models to ensure they are registered in SQLAlchemy
from app.users.infrastructure.models import UserORM
from app.contracts.infrastructure.models import ContractORM
from app.forecastSystems.infrastructure.models import ForecastSystemORM
from app.ports.infrastructure.models import PortORM
from app.hindcastPoint.infrastructure.models import HindcastPointORM
from app.forecast_zones.infrastructure.models import ForecastZoneORM
from app.forecast_system_results.infrastructure.models import ForecastSystemResultORM
from app.downloadData.infrastructure.models import DownloadedDataORM

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