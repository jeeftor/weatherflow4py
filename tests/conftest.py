import json
import pytest


@pytest.fixture
def forecast_json():
    # Load your sample JSON data
    with open("fixtures/forecast.json", "r") as json_file:
        data = json.load(json_file)
    return data
