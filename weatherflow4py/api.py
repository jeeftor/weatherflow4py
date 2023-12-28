import httpx

from weatherflow4py.models.forecast import WeatherData
from weatherflow4py.models.station import StationsResponse


class WeatherFlowRestAPI:
    BASE_URL = "https://swd.weatherflow.com/swd/rest"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = httpx.AsyncClient(headers={"Accept": "application/json"})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(
        self, endpoint: str, params: dict = None, response_model=None
    ):
        url = f"{self.BASE_URL}/{endpoint}"
        full_params = {"token": self.api_token, **(params or {})}
        response = await self.client.get(url, params=full_params)
        response.raise_for_status()
        return (
            response_model.from_json(response.text)
            if response_model
            else response.json()
        )

    async def async_get_stations(self) -> StationsResponse:
        return (
            await self._make_request("stations", response_model=StationsResponse)
        ).stations

    async def async_get_station(self, station_id: int) -> StationsResponse:
        return (
            await self._make_request(
                f"stations/{station_id}", response_model=StationsResponse
            )
        ).stations

    async def async_get_forecast(self, station_id: int):
        return await self._make_request(
            "better_forecast",
            params={"station_id": station_id},
            response_model=WeatherData,
        )
