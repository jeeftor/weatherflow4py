import pytest

from weatherflow4py.models.forecast import (
    WeatherData,
    Forecast,
    CurrentConditions,
    Units,
)


def test_convert_json_to_weather_data(forecast_json):
    try:
        weather_data = WeatherData.from_dict(forecast_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to WeatherData: {e}")

        # Assert that the conversion was successful
    assert isinstance(weather_data, WeatherData)

    assert isinstance(weather_data.current_conditions, CurrentConditions)
    assert isinstance(weather_data.forecast, Forecast)
    assert isinstance(weather_data.latitude, float)
    assert isinstance(weather_data.longitude, float)
    assert isinstance(weather_data.location_name, str)
    assert isinstance(weather_data.timezone, str)
    assert isinstance(weather_data.timezone_offset_minutes, int)
    assert isinstance(weather_data.units, Units)
