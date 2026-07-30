import asyncio, json
from sqlalchemy.ext.asyncio import create_async_engine
from app.shared.config import settings

async def fix():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.execute(
            __import__('sqlalchemy').text(
                "UPDATE hindcast_points SET wind_url = :url, wind_models = :models WHERE id = 1"
            ),
            {"url": "https://api.open-meteo.com/v1/forecast", "models": json.dumps(["best_match"])}
        )
        print("Updated hindcast_point id=1 with wind_url")
    await engine.dispose()

asyncio.run(fix())
