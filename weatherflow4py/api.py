from typing import Optional

import aiohttp

from weatherflow4py.exceptions import TokenError
from weatherflow4py.models.rest.device import DeviceObservationTempestREST
from weatherflow4py.models.rest.forecast import WeatherDataForecastREST
from weatherflow4py.models.rest.observation import ObservationStationREST
from weatherflow4py.models.rest.stations import StationsResponseREST
from weatherflow4py.models.rest.unified import WeatherFlowDataREST
from .const import REST_LOGGER

from yarl import URL


class WeatherFlowRestAPI:
    """Our REST rate limits are not connected to our web socket rate limits. For REST you can make 100 requests per
    minute. There is some burst capacity built into the system, but the general rule of thumb it to keep the number
    of REST requests per user to under 100 per minute."""

    BASE_URL = "https://swd.weatherflow.com/swd/rest"

    def __init__(self, api_token: str, session: Optional[aiohttp.ClientSession] = None):
        if not api_token:
            raise TokenError

        REST_LOGGER.debug(f"Initializing the WeatherFlow API with token {api_token}")
        self.api_token = api_token
        self._session = session
        self._owned_session = None

    @property
    def session(self):
        if self._session is None:
            if self._owned_session is None:
                self._owned_session = aiohttp.ClientSession(
                    headers={"Accept": "application/json"}
                )
            return self._owned_session
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Do not close the session here
        pass

    async def _make_request(
        self, endpoint: str, params: dict = None, response_model=None
    ):
        url = URL(f"{self.BASE_URL}/{endpoint}")
        full_params = {"token": self.api_token, **(params or {})}
        full_url = url.with_query(full_params)

        REST_LOGGER.debug(f"Making request to {full_url}")

        async with self.session.get(url, params=full_params) as response:
            response.raise_for_status()
            data = await response.text()

            REST_LOGGER.debug(f"Received response: {data}")

        try:
            return response_model.from_json(data) if response_model else None
        except Exception as e:
            error_msg = f"Unable to convert data || {data} || to || {response_model} -- {str(e)}"
            print(error_msg)
            REST_LOGGER.error(error_msg)
            raise e

    async def async_get_stations(self) -> StationsResponseREST:
        """
        Gets station_id data.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        ret = await self._make_request("stations", response_model=StationsResponseREST)
        return ret

    async def async_get_station(self, station_id: int) -> StationsResponseREST:
        """
        Gets data for a specific station_id.

        Args:
            station_id (int): The ID of the station_id.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return (
            await self._make_request(
                f"stations/{station_id}", response_model=StationsResponseREST
            )
        ).stations

    async def async_get_forecast(self, station_id: int) -> WeatherDataForecastREST:
        """
        Gets the forecast for a given station_id.

        Args:
            station_id (int): The ID of the station_id.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return await self._make_request(
            "better_forecast",
            params={"station_id": station_id},
            response_model=WeatherDataForecastREST,
        )

    async def async_get_device_observations(
        self, device_id: int
    ) -> DeviceObservationTempestREST:
        """
        Gets the device_id observation data for a given device_id.

        Args:
            device_id (int): The ID of the device_id.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        obs_data = await self._make_request(
            f"observations/device/{device_id}",
            response_model=DeviceObservationTempestREST,
        )

        return obs_data

    async def async_get_observation(self, station_id: int) -> ObservationStationREST:
        """
        Gets the observation data for a given station_id.

        Args:
            station_id (int): The ID of the station_id.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return await self._make_request(
            f"observations/station/{station_id}",
            response_model=ObservationStationREST,
        )

    async def get_all_data(
        self, get_device_observations: bool = False
    ) -> dict[int, WeatherFlowDataREST]:
        """
        Builds a full data set of stations and forecasts. If get_device_observations is True,
        it also fetches device_id observations for each station_id. Otherwise, device_observations
        will be set to None for each station_id.

        Args:
            get_device_observations (bool): Whether to fetch device_id observations for each station_id.

        Returns:
            dict[int, WeatherFlowDataREST]: A dictionary mapping station_id IDs to their corresponding data.

        Raises:
            ClientResponseError: If there is a client response error during data retrieval.
        """
        ret: dict[int, WeatherFlowDataREST] = {}
        station_response = await self.async_get_stations()
        for station in station_response.stations:
            device_id = station.outdoor_devices[0].device_id

            device_observations = None
            if get_device_observations:
                device_observations = await self.async_get_device_observations(
                    device_id=device_id
                )

            ret[station.station_id] = WeatherFlowDataREST(
                weather=await self.async_get_forecast(station_id=station.station_id),
                observation=await self.async_get_observation(
                    station_id=station.station_id
                ),
                station=station,
                device_observations=device_observations,
            )

        return ret

    @classmethod
    async def create(
        cls, api_token: str, session: Optional[aiohttp.ClientSession] = None
    ):
        return cls(api_token, session)

    async def close(self):
        if self._owned_session:
            await self._owned_session.close()
            self._owned_session = None
