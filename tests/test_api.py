import pytest
from aioresponses import aioresponses  # Make sure to import aioresponses

from weatherflow4py.api import WeatherFlowRestAPI
from weatherflow4py.exceptions import TokenError
from weatherflow4py.models.forecast import WeatherData
from aiohttp import ClientResponseError


@pytest.mark.asyncio
async def test_api_calls(forecast_json, station_json, stations_json):
    with aioresponses() as mock:
        mock.get(
            "https://swd.weatherflow.com/swd/rest/stations?token=mock_token",
            payload=stations_json,
        )
        mock.get(
            " https://swd.weatherflow.com/swd/rest/better_forecast?station_id=24432&token=mock_token",
            payload=forecast_json,
        )

        async with WeatherFlowRestAPI("mock_token") as api:
            stations = await api.async_get_stations()
            for station in stations:
                assert station.name == "My Home Station"
                assert station.station_id == 24432

                assert station.latitude == 43.94962
                assert station.longitude == -102.86831
                assert station.elevation == 2063.150146484375
                forecast = await api.async_get_forecast(station_id=station.station_id)
                assert isinstance(forecast, WeatherData)


@pytest.mark.asyncio
async def test_api_calls_unauthorized(unauthorized_json):
    with aioresponses() as mock:
        mock.get(
            "https://swd.weatherflow.com/swd/rest/stations?token=mock_token",
            payload=unauthorized_json,
            status=401,
        )

        async with WeatherFlowRestAPI("mock_token") as api:
            # Expect an HTTPUnauthorized exception
            with pytest.raises(ClientResponseError):
                await api.async_get_stations()


@pytest.mark.asyncio
async def test_bad_token():
    with pytest.raises(TokenError):
        token: str = None
        WeatherFlowRestAPI(token)
