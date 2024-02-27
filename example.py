import asyncio
import os

from weatherflow4py.api import WeatherFlowRestAPI
from dotenv import load_dotenv


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    async with WeatherFlowRestAPI(token) as api:
        data = await api.get_all_data()
        print(data)

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

            obs = await api.async_get_observation(station_id=station.station_id)
            print(obs)

            print(obs.obs[0].air_temperature)

            device_obs = await api.async_get_device_observations(
                station.outdoor_devices[0].device_id
            )
            print(device_obs.precipitation_type)


if __name__ == "__main__":
    asyncio.run(main())
