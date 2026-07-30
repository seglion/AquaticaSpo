import httpx, asyncio
async def t():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 43.875,
        "longitude": -7.2083282,
        "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "models": "best_match",
    }
    async with httpx.AsyncClient() as c:
        r = await c.get(url, params=params)
        print(f"Status: {r.status_code}")
        data = r.json()
        hourly = data.get("hourly", {})
        print(f"Keys in hourly: {list(hourly.keys())}")
        print(f"Sample wind_speed_10m (first 3): {hourly['wind_speed_10m'][:3]}")
        print(f"lat={data.get('latitude')}, lon={data.get('longitude')}")
asyncio.run(t())
