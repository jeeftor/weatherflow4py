import json

import pytest

from weatherflow4py.models.ws.custom_types import PrecipitationType
from weatherflow4py.models.rest.device import (
    DeviceObservationTempestREST,
    PrecipitationAnalysisType,
)
from weatherflow4py.models.rest.forecast import (
    WeatherData,
    Forecast,
    CurrentConditions,
    ForecastUnits,
)
from weatherflow4py.models.ws.obs import ObservationType
from weatherflow4py.models.rest.observation import StationObservation


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


def test_convert_json_to_observation2(observation2_json):
    try:
        obs_data = StationObservation.from_dict(observation2_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to Observation: {e}")

    assert isinstance(obs_data, StationObservation)
    assert obs_data.elevation == observation2_json["elevation"]
    assert obs_data.is_public == observation2_json["is_public"]
    assert obs_data.latitude == observation2_json["latitude"]
    assert obs_data.longitude == observation2_json["longitude"]
    assert obs_data.public_name == observation2_json["public_name"]
    assert obs_data.station_id == observation2_json["station_id"]
    assert obs_data.station_name == observation2_json["station_name"]
    assert obs_data.timezone == observation2_json["timezone"]

    for obs, obs_json in zip(obs_data.obs, observation2_json["obs"]):
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
        assert obs.precip_accum_local_day_final == 0
        assert (
            obs.precip_accum_local_yesterday == obs_json["precip_accum_local_yesterday"]
        )
        assert obs.precip_accum_local_yesterday_final == 0
        assert (
            obs.precip_analysis_type_yesterday
            == obs_json["precip_analysis_type_yesterday"]
        )
        assert obs.precip_minutes_local_day == obs_json["precip_minutes_local_day"]
        assert (
            obs.precip_minutes_local_yesterday
            == obs_json["precip_minutes_local_yesterday"]
        )
        assert obs.precip_minutes_local_yesterday_final == 0
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
    assert isinstance(weather_data.units, ForecastUnits)


def test_convert_json_to_weather_data2(forecast2_json):
    try:
        weather_data = WeatherData.from_dict(forecast2_json)
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
    assert isinstance(weather_data.units, ForecastUnits)


def test_convert_weather_data_ha_forecast(forecast_json):
    try:
        weather_data = WeatherData.from_dict(forecast_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to WeatherData: {e}")

    forecasts = [x.ha_forecast for x in weather_data.forecast.daily]
    print(forecasts)


def test_obs_st(obs_st_json):
    obs_json = DeviceObservationTempestREST.from_json(json.dumps(obs_st_json))
    obs_dict = DeviceObservationTempestREST.from_dict(obs_st_json)

    assert obs_dict == obs_json

    try:
        obs_st = DeviceObservationTempestREST.from_dict(obs_st_json)
    except Exception as e:
        pytest.fail(f"Failed to convert JSON data to ObsSky: {e}")

    assert isinstance(obs_st, DeviceObservationTempestREST)

    assert obs_st.epoch == 1709057252
    assert obs_st.wind_lull == 0.77
    assert obs_st.wind_avg == 2.07
    assert obs_st.wind_gust == 3.98
    assert obs_st.wind_direction == 58
    assert obs_st.wind_sample_interval == obs_st_json["obs"][0][5]
    assert obs_st.pressure == obs_st_json["obs"][0][6]
    assert obs_st.air_temperature == obs_st_json["obs"][0][7]

    assert obs_st.status.status_code == obs_st_json["status"]["status_code"]
    assert obs_st.status.status_message == obs_st_json["status"]["status_message"]
    assert obs_st.device_id == obs_st_json["device_id"]
    assert obs_st.type == ObservationType.OBS_ST
    assert obs_st.source == obs_st_json["source"]
    assert obs_st.summary.pressure_trend == obs_st_json["summary"]["pressure_trend"]
    assert obs_st.summary.strike_count_1h == obs_st_json["summary"]["strike_count_1h"]
    assert obs_st.summary.strike_count_3h == obs_st_json["summary"]["strike_count_3h"]
    assert obs_st.summary.precip_total_1h == obs_st_json["summary"]["precip_total_1h"]
    assert obs_st.summary.strike_last_dist == obs_st_json["summary"]["strike_last_dist"]
    assert (
        obs_st.summary.strike_last_epoch == obs_st_json["summary"]["strike_last_epoch"]
    )
    assert (
        obs_st.summary.precip_accum_local_yesterday
        == obs_st_json["summary"]["precip_accum_local_yesterday"]
    )
    assert (
        obs_st.summary.precip_accum_local_yesterday_final
        == obs_st_json["summary"]["precip_accum_local_yesterday_final"]
    )
    assert (
        obs_st.summary.precip_analysis_type_yesterday == PrecipitationAnalysisType.NONE
    )
    assert obs_st.summary.feels_like == obs_st_json["summary"]["feels_like"]
    assert obs_st.summary.heat_index == obs_st_json["summary"]["heat_index"]
    assert obs_st.summary.wind_chill == obs_st_json["summary"]["wind_chill"]
    assert obs_st.epoch == obs_st_json["obs"][0][0]
    assert obs_st.wind_lull == obs_st_json["obs"][0][1]
    assert obs_st.wind_avg == obs_st_json["obs"][0][2]
    assert obs_st.wind_gust == obs_st_json["obs"][0][3]
    assert obs_st.wind_direction == obs_st_json["obs"][0][4]
    assert obs_st.wind_sample_interval == obs_st_json["obs"][0][5]
    assert obs_st.pressure == obs_st_json["obs"][0][6]
    assert obs_st.air_temperature == obs_st_json["obs"][0][7]
    assert obs_st.relative_humidity == obs_st_json["obs"][0][8]
    assert obs_st.illuminance == obs_st_json["obs"][0][9]
    assert obs_st.uv == obs_st_json["obs"][0][10]
    assert obs_st.solar_radiation == obs_st_json["obs"][0][11]
    assert obs_st.rain_accumulation == obs_st_json["obs"][0][12]
    assert obs_st.precipitation_type == PrecipitationType.NONE
    assert obs_st.average_strike_distance == obs_st_json["obs"][0][14]
    assert obs_st.strike_count == obs_st_json["obs"][0][15]
    assert obs_st.battery == obs_st_json["obs"][0][16]
    assert obs_st.report_interval == obs_st_json["obs"][0][17]
    assert obs_st.local_day_rain_accumulation == obs_st_json["obs"][0][18]
    assert obs_st.nc_rain_accumulation == obs_st_json["obs"][0][19]
    assert obs_st.local_day_nc_rain_accumulation == obs_st_json["obs"][0][20]
    assert obs_st.precipitation_analysis_type == PrecipitationAnalysisType.NONE
