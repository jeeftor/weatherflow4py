import json
import os

import pytest
from aioresponses import aioresponses
from weatherflow4py.api import WeatherFlowRestAPI

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def websocket_messages() -> list:
    """Load the websocket_messages.json fixture file."""
    with open(
        os.path.join(dir_path, "fixtures/websocket_messages.json"), "r"
    ) as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def websocket_winds() -> list:
    with open(os.path.join(dir_path, "fixtures/ws_winds.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def ws_obs_air() -> dict:
    """Load the ws_obs_air.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/ws_obs_air.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def ws_obs_sky() -> dict:
    """Load the ws_obs_sky.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/ws_obs_sky.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def ws_obs_st() -> dict:
    """Load the ws_obs_st.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/ws_obs_st.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def ws_obs_st_3x() -> dict:
    """Load the ws_obs_st_3x.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/ws_obs_st_3x.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def obs_st_json() -> dict:
    """Load the obs_st.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/obs_st.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def forecast_json() -> dict:
    """Load the forecast.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/forecast.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def forecast2_json() -> dict:
    """Load the forecast.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/forecast2.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def observation_json() -> dict:
    with open(os.path.join(dir_path, "fixtures/observation.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def unauthorized_json() -> dict:
    """Load the forecast.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/401.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def station_json() -> dict:
    """Load the station.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/station.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
def stations_json() -> dict:
    """Load the stations.json fixture file."""
    with open(os.path.join(dir_path, "fixtures/stations.json"), "r") as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture
async def mock_aioresponse(
    forecast_json, station_json, stations_json, observation_json
):
    with aioresponses() as m:
        # Setup mock responses here or leave it to be configured in the test functions
        yield m


@pytest.fixture
async def weather_api():
    api = WeatherFlowRestAPI("your_api_token")
    async with api as api_instance:
        yield api_instance
