import asyncio
import os

from weatherflow4py.api import WeatherFlowRestAPI


async def main():
    token = os.getenv("API_TOKEN")
    async with WeatherFlowRestAPI(token) as api:
        stations = await api.async_get_stations()
        for station in stations:
            print(station.name)
            print(station.station_id)
            print(station.public_name)
            print(station.latitude)
            print(station.longitude)
            print(station.elevation)
            print(station.devices)
            print("\n")
            forecast = await api.async_get_forecast(station_id=station.station_id)
            print(forecast.units)

            # Hash Testing


if __name__ == "__main__":
    asyncio.run(main())
