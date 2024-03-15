import pytest
from aioresponses import aioresponses  # Make sure to import aioresponses

from weatherflow4py.api import WeatherFlowRestAPI
from weatherflow4py.exceptions import TokenError
from weatherflow4py.models.rest.device import DeviceObservationREST
from weatherflow4py.models.rest.forecast import WeatherDataForecastREST
from aiohttp import ClientResponseError

from weatherflow4py.models.rest.stations import StationsResponseREST
from weatherflow4py.models.rest.unified import WeatherFlowDataREST


@pytest.mark.asyncio
async def test_api_calls(
    rest_betterforecast_1,
    rest_station_json,
    rest_stations_json,
    rest_station_observation2,
    rest_device_observation_1,
):
    import logging

    logging.basicConfig(level=logging.DEBUG)

    with aioresponses() as mock:
        mock.get(
            "https://swd.weatherflow.com/swd/rest/stations?token=mock_token",
            payload=rest_stations_json,
        )
        mock.get(
            "https://swd.weatherflow.com/swd/rest/better_forecast?station_id=24432&token=mock_token",
            payload=rest_betterforecast_1,
        )
        mock.get(
            "https://swd.weatherflow.com/swd/rest/observations/station?station_id=24432&token=mock_token",
            payload=rest_station_json,
        )

        mock.get(
            "https://swd.weatherflow.com/swd/rest/observations/device/123456?token=mock_token",
            payload=rest_device_observation_1,
        )
        mock.get(
            "https://swd.weatherflow.com/swd/rest/observations/station/24432?token=mock_token",
            payload=rest_station_observation2,
        )

        sor = StationsResponseREST.from_dict(rest_stations_json)
        assert isinstance(sor, StationsResponseREST)
        sor2 = StationsResponseREST.from_dict(rest_station_json)
        assert isinstance(sor2, StationsResponseREST)

        dob = DeviceObservationREST.from_dict(rest_device_observation_1)
        assert isinstance(dob, DeviceObservationREST)
        wf = WeatherDataForecastREST.from_dict(rest_betterforecast_1)
        assert isinstance(wf, WeatherDataForecastREST)

        async with WeatherFlowRestAPI("mock_token") as api:
            data: WeatherFlowDataREST = await api.get_all_data(
                get_device_observations=True
            )
            assert data[24432].station.station_id == 24432


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
