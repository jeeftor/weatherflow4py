import json
from typing import Any, Self

import pytest
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from weatherflow4py.api import WeatherFlowRestAPI
from weatherflow4py.exceptions import TokenError
from weatherflow4py.models.rest.device import DeviceObservationREST
from weatherflow4py.models.rest.forecast import WeatherDataForecastREST

from weatherflow4py.models.rest.stations import StationsResponseREST
from weatherflow4py.models.rest.unified import WeatherFlowDataREST


class FakeResponse:
    def __init__(self, url: str, payload: dict[str, Any], status: int = 200) -> None:
        self.url = URL(url)
        self.payload = payload
        self.status = status

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.status < 400:
            return
        request_info = RequestInfo(
            url=self.url,
            method="GET",
            headers=CIMultiDictProxy(CIMultiDict()),
            real_url=self.url,
        )
        raise ClientResponseError(
            request_info=request_info,
            history=(),
            status=self.status,
            message="Unauthorized",
        )

    async def text(self) -> str:
        return json.dumps(self.payload)


class FakeSession:
    def __init__(self) -> None:
        self.responses: dict[
            tuple[str, tuple[tuple[str, str], ...]], tuple[dict[str, Any], int]
        ] = {}

    def add(self, url: str, payload: dict[str, Any], status: int = 200) -> None:
        parsed_url = URL(url)
        self.responses[self._key(parsed_url)] = (payload, status)

    def get(self, url: URL, params: dict[str, Any]) -> FakeResponse:
        request_url = url.with_query(params)
        payload, status = self.responses[self._key(request_url)]
        return FakeResponse(str(request_url), payload, status)

    @staticmethod
    def _key(url: URL) -> tuple[str, tuple[tuple[str, str], ...]]:
        base_url = str(url.with_query({}))
        query = tuple(sorted(url.query.items()))
        return base_url, query


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

    session = FakeSession()
    session.add(
        "https://swd.weatherflow.com/swd/rest/stations?token=mock_token",
        rest_stations_json,
    )
    session.add(
        "https://swd.weatherflow.com/swd/rest/better_forecast?station_id=24432&token=mock_token",
        rest_betterforecast_1,
    )
    session.add(
        "https://swd.weatherflow.com/swd/rest/observations/station?station_id=24432&token=mock_token",
        rest_station_json,
    )
    session.add(
        "https://swd.weatherflow.com/swd/rest/observations/device/123456?token=mock_token",
        rest_device_observation_1,
    )
    session.add(
        "https://swd.weatherflow.com/swd/rest/observations/station/24432?token=mock_token",
        rest_station_observation2,
    )

    sor = StationsResponseREST.from_dict(rest_stations_json)
    assert isinstance(sor, StationsResponseREST)
    sor2 = StationsResponseREST.from_dict(rest_station_json)
    assert isinstance(sor2, StationsResponseREST)

    dob = DeviceObservationREST.from_dict(rest_device_observation_1)
    assert isinstance(dob, DeviceObservationREST)
    wf = WeatherDataForecastREST.from_dict(rest_betterforecast_1)
    assert isinstance(wf, WeatherDataForecastREST)

    async with WeatherFlowRestAPI("mock_token", session=session) as api:
        data: WeatherFlowDataREST = await api.get_all_data(get_device_observations=True)

        assert data[24432].station.station_id == 24432


@pytest.mark.asyncio
async def test_api_calls_unauthorized(unauthorized_json):
    session = FakeSession()
    session.add(
        "https://swd.weatherflow.com/swd/rest/stations?token=mock_token",
        unauthorized_json,
        status=401,
    )

    async with WeatherFlowRestAPI("mock_token", session=session) as api:
        # Expect an HTTPUnauthorized exception
        with pytest.raises(ClientResponseError):
            await api.async_get_stations()


@pytest.mark.asyncio
async def test_bad_token():
    with pytest.raises(TokenError):
        WeatherFlowRestAPI(None)  # type: ignore
