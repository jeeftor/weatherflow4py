import json
import pytest
from aioresponses import aioresponses
from weatherflow4py.api import WeatherFlowRestAPI


@pytest.fixture
def forecast_json() -> dict:
    """Load the forecast.json fixture file."""
    with open("fixtures/forecast.json", "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def unauthorized_json() -> dict:
    """Load the forecast.json fixture file."""
    with open("fixtures/401.json", "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def station_json() -> dict:
    """Load the station.json fixture file."""
    with open("fixtures/station.json", "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def stations_json() -> dict:
    """Load the stations.json fixture file."""
    with open("fixtures/stations.json", "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
async def mock_aioresponse(forecast_json, station_json, stations_json):
    with aioresponses() as m:
        # Setup mock responses here or leave it to be configured in the test functions
        yield m


@pytest.fixture
async def weather_api():
    api = WeatherFlowRestAPI("your_api_token")
    async with api as api_instance:
        yield api_instance
