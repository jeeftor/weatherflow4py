import pytest

from weatherflow4py.models.forecast import (
    WeatherData,
    Forecast,
    CurrentConditions,
    Units,
)
from weatherflow4py.models.observation import StationObservation


def test_convert_json_to_observation(observation_json):
    try:
        obs_data = StationObservation.from_dict(observation_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to Observation: {e}")

    assert isinstance(obs_data, StationObservation)
    assert obs_data.elevation == observation_json["elevation"]
    assert obs_data.is_public == observation_json["is_public"]
    assert obs_data.latitude == observation_json["latitude"]
    assert obs_data.longitude == observation_json["longitude"]
    assert obs_data.public_name == observation_json["public_name"]
    assert obs_data.station_id == observation_json["station_id"]
    assert obs_data.station_name == observation_json["station_name"]
    assert obs_data.timezone == observation_json["timezone"]

    for obs, obs_json in zip(obs_data.obs, observation_json["obs"]):
        assert obs.air_density == obs_json["air_density"]
        assert obs.air_temperature == obs_json["air_temperature"]
        assert obs.barometric_pressure == obs_json["barometric_pressure"]
        assert obs.brightness == obs_json["brightness"]
        assert obs.delta_t == obs_json["delta_t"]
        assert obs.dew_point == obs_json["dew_point"]
        assert obs.feels_like == obs_json["feels_like"]
        assert obs.heat_index == obs_json["heat_index"]
        assert obs.lightning_strike_count == obs_json["lightning_strike_count"]
        assert (
            obs.lightning_strike_count_last_1hr
            == obs_json["lightning_strike_count_last_1hr"]
        )
        assert (
            obs.lightning_strike_count_last_3hr
            == obs_json["lightning_strike_count_last_3hr"]
        )
        assert (
            obs.lightning_strike_last_distance
            == obs_json["lightning_strike_last_distance"]
        )
        assert (
            obs.lightning_strike_last_epoch == obs_json["lightning_strike_last_epoch"]
        )
        assert obs.precip == obs_json["precip"]
        assert obs.precip_accum_last_1hr == obs_json["precip_accum_last_1hr"]
        assert obs.precip_accum_local_day == obs_json["precip_accum_local_day"]
        assert (
            obs.precip_accum_local_day_final == obs_json["precip_accum_local_day_final"]
        )
        assert (
            obs.precip_accum_local_yesterday == obs_json["precip_accum_local_yesterday"]
        )
        assert (
            obs.precip_accum_local_yesterday_final
            == obs_json["precip_accum_local_yesterday_final"]
        )
        assert (
            obs.precip_analysis_type_yesterday
            == obs_json["precip_analysis_type_yesterday"]
        )
        assert obs.precip_minutes_local_day == obs_json["precip_minutes_local_day"]
        assert (
            obs.precip_minutes_local_yesterday
            == obs_json["precip_minutes_local_yesterday"]
        )
        assert (
            obs.precip_minutes_local_yesterday_final
            == obs_json["precip_minutes_local_yesterday_final"]
        )
        assert obs.pressure_trend == obs_json["pressure_trend"]
        assert obs.relative_humidity == obs_json["relative_humidity"]
        assert obs.sea_level_pressure == obs_json["sea_level_pressure"]
        assert obs.solar_radiation == obs_json["solar_radiation"]
        assert obs.station_pressure == obs_json["station_pressure"]
        assert obs.timestamp == obs_json["timestamp"]
        assert obs.uv == obs_json["uv"]
        assert obs.wet_bulb_globe_temperature == obs_json["wet_bulb_globe_temperature"]
        assert obs.wet_bulb_temperature == obs_json["wet_bulb_temperature"]
        assert obs.wind_avg == obs_json["wind_avg"]
        assert obs.wind_chill == obs_json["wind_chill"]
        assert obs.wind_direction == obs_json["wind_direction"]
        assert obs.wind_gust == obs_json["wind_gust"]
        assert obs.wind_lull == obs_json["wind_lull"]


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


def test_convert_weather_data_ha_forecast(forecast_json):
    try:
        weather_data = WeatherData.from_dict(forecast_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to WeatherData: {e}")

    forecasts = [x.ha_forecast for x in weather_data.forecast.daily]
    print(forecasts)
