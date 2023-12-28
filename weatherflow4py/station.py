import httpx

from weatherflow4py.models import StationsResponse


async def async_get_stations(api_token: str) -> StationsResponse:
    url = "https://swd.weatherflow.com/swd/rest/stations"
    headers = {"Accept": "application/json"}
    params = {"token": api_token}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
        return StationsResponse.from_json(response.text)
