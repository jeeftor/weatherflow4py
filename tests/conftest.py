import json
import os

import pytest
from aioresponses import aioresponses
from weatherflow4py.api import WeatherFlowRestAPI

dir_path = os.path.dirname(os.path.realpath(__file__))


def load_fixture(file_name):
    with open(os.path.join(dir_path, file_name), "r") as json_file:
        return json.load(json_file)


@pytest.fixture
def websocket_messages():
    return load_fixture("fixtures/ws/websocket_messages.json")


@pytest.fixture
def websocket_winds():
    return load_fixture("fixtures/ws/ws_winds.json")


@pytest.fixture
def websocket_strike():
    return load_fixture("fixtures/ws/ws_strike.json")


@pytest.fixture
def ws_obs_air():
    return load_fixture("fixtures/ws_obs_air.json")


@pytest.fixture
def ws_obs_sky():
    return load_fixture("fixtures/ws_obs_sky.json")


@pytest.fixture
def ws_obs_st():
    return load_fixture("fixtures/ws_obs_st.json")


@pytest.fixture
def ws_obs_st_3x():
    return load_fixture("fixtures/ws_obs_st_3x.json")


@pytest.fixture
def obs_st_json():
    return load_fixture("fixtures/obs_st.json")


@pytest.fixture
def rest_betterforecast_1():
    return load_fixture("fixtures/rest/betterforecast/forecast.json")


@pytest.fixture
def rest_betterforecast_2():
    return load_fixture("fixtures/rest/betterforecast/forecast2.json")


@pytest.fixture
def rest_betterforecast_3():
    return load_fixture("fixtures/rest/betterforecast/forecast3.json")


@pytest.fixture
def rest_betterforecast_4():
    return load_fixture("fixtures/rest/betterforecast/forecast4.json")


@pytest.fixture
def rest_betterforecast_5():
    return load_fixture("fixtures/rest/betterforecast/forecast5.json")


@pytest.fixture
def rest_betterforecast_6():
    return load_fixture("fixtures/rest/betterforecast/forecast6.json")


@pytest.fixture
def rest_station_observation1():
    return load_fixture(
        "fixtures/rest/observations/station_id/station_observation1.json"
    )


@pytest.fixture
def rest_station_observation2():
    return load_fixture(
        "fixtures/rest/observations/station_id/station_observation2.json"
    )


@pytest.fixture
def rest_device_observation_1():
    return load_fixture("fixtures/rest/observations/device_id/1.json")


@pytest.fixture
def rest_device_observation_2():
    return load_fixture("fixtures/rest/observations/device_id/2.json")


@pytest.fixture
def unauthorized_json():
    return load_fixture("fixtures/rest/401.json")


@pytest.fixture
def rest_internal_error_json():
    return load_fixture("fixtures/rest/internal_error.json")


@pytest.fixture
def rest_station_json():
    return load_fixture("fixtures/rest/stations/station_id/station_id.json")


@pytest.fixture
def rest_stations_json():
    return load_fixture("fixtures/rest/stations/stations.json")


@pytest.fixture
def rest_stations_with_errors_json():
    return load_fixture("fixtures/rest/stations/stations_with_errors.json")


@pytest.fixture
async def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture
async def weather_api():
    api = WeatherFlowRestAPI("your_api_token")
    async with api as api_instance:
        yield api_instance
