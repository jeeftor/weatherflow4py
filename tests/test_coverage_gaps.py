"""Targeted tests to cover remaining gaps in observation.py, websocket_response.py, and api.py."""

from __future__ import annotations

import pytest

from weatherflow4py.models.rest.observation import (
    Observation,
    StationStatus,
    WetBulbFlag,
)
from weatherflow4py.models.ws.websocket_response import (
    BaseResponseWS,
    EventDataLightningStrike,
    EventDataRapidWind,
    LightningStrikeEventWS,
    WebsocketResponseBuilder,
)


# ---------------------------------------------------------------------------
# ObservationREST – precip aliases (lines 73, 78, 83)
# ---------------------------------------------------------------------------


def _make_obs(**kwargs) -> Observation:
    """Build a minimal ObservationREST with sensible defaults."""
    defaults = dict(
        timestamp=1709057252,
        air_temperature=20.0,
        barometric_pressure=1013.0,
        station_pressure=1013.0,
        sea_level_pressure=1013.0,
        relative_humidity=65,
        precip=0.0,
        precip_accum_last_1hr=0.0,
        precip_accum_local_day=0.0,
        precip_accum_local_day_final=1.5,
        precip_accum_local_yesterday=0.0,
        precip_accum_local_yesterday_final=2.0,
        precip_analysis_type_yesterday=0,
        precip_minutes_local_day=0,
        precip_minutes_local_yesterday=5,
        precip_minutes_local_yesterday_final=6,
        wind_avg=2.0,
        wind_direction=90,
        wind_gust=4.0,
        wind_lull=0.5,
        wind_chill=18.0,
        feels_like=19.0,
        heat_index=20.0,
        dew_point=12.0,
        wet_bulb_temperature=15.0,
        wet_bulb_globe_temperature=20.0,
        delta_t=5.0,
        air_density=1.2,
        solar_radiation=500,
        uv=6.0,
        brightness=10000,
        lightning_strike_last_epoch=None,
        lightning_strike_last_distance=0,
        lightning_strike_count=0,
        lightning_strike_count_last_1hr=0,
        lightning_strike_count_last_3hr=0,
        pressure_trend="steady",
    )
    defaults.update(kwargs)
    return Observation(**defaults)


def test_precip_accum_local_day_nearcast_alias():
    obs = _make_obs(precip_accum_local_day_final=3.7)
    assert obs.precip_accum_local_day_nearcast == 3.7


def test_precip_accum_local_yesterday_nearcast_alias():
    obs = _make_obs(precip_accum_local_yesterday_final=1.1)
    assert obs.precip_accum_local_yesterday_nearcast == 1.1


def test_precip_minutes_local_yesterday_nearcast_alias():
    obs = _make_obs(precip_minutes_local_yesterday_final=9)
    assert obs.precip_minutes_local_yesterday_nearcast == 9


# ---------------------------------------------------------------------------
# ObservationREST – wet_bulb_globe_temperature_category (lines 115-126)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wbgt, expected_category, expected_flag",
    [
        (20.0, 0, WetBulbFlag.NONE),  # <= 25.6
        (26.0, 1, WetBulbFlag.WHITE),  # <= 27.7
        (28.0, 2, WetBulbFlag.GREEN),  # <= 29.4
        (30.0, 3, WetBulbFlag.YELLOW),  # <= 31.0
        (31.5, 4, WetBulbFlag.RED),  # <= 32.1
        (33.0, 5, WetBulbFlag.BLACK),  # > 32.1
    ],
)
def test_wet_bulb_globe_temperature_category(wbgt, expected_category, expected_flag):
    obs = _make_obs(wet_bulb_globe_temperature=wbgt)
    assert obs.wet_bulb_globe_temperature_category == expected_category
    assert obs.wet_bulb_globe_temperature_flag == expected_flag


def test_wet_bulb_globe_temperature_none_returns_none_category():
    obs = _make_obs(wet_bulb_globe_temperature=None)
    assert obs.wet_bulb_globe_temperature_category is None


def test_wet_bulb_globe_temperature_flag_none():
    obs = _make_obs(wet_bulb_globe_temperature=None)
    assert obs.wet_bulb_globe_temperature_flag is None


# ---------------------------------------------------------------------------
# ObservationREST – uv_index_color and uv_index_exposure (lines 140-158)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "uv, expected_color, expected_exposure",
    [
        (1.0, "green", "low"),  # <= 2
        (3.0, "yellow", "moderate"),  # <= 5
        (6.0, "orange", "high"),  # <= 7
        (9.0, "red", "very high"),  # <= 10
        (11.0, "purple", "extreme"),  # > 10
    ],
)
def test_uv_index_color_and_exposure(uv, expected_color, expected_exposure):
    obs = _make_obs(uv=uv)
    assert obs.uv_index_color == expected_color
    assert obs.uv_index_exposure == expected_exposure


# ---------------------------------------------------------------------------
# StationStatus – offline debug log path (line 187)
# ---------------------------------------------------------------------------


def test_station_status_offline_message(caplog):
    import logging

    with caplog.at_level(logging.DEBUG):
        StationStatus(
            status_code=0,
            status_message="SUCCESS - Either no capabilities or no recent observations",
        )
    assert any("offline" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# BaseResponseWS – __eq__ (lines 27-29)
# ---------------------------------------------------------------------------


def test_base_response_ws_eq_different_type():
    resp = BaseResponseWS.from_dict({"type": "ack", "id": "x"})  # type: ignore
    assert resp.__eq__("not_a_ws_object") is NotImplemented


def test_base_response_ws_eq_same():
    resp1 = BaseResponseWS.from_dict({"type": "ack", "id": "x"})  # type: ignore
    resp2 = BaseResponseWS.from_dict({"type": "ack", "id": "x"})  # type: ignore
    assert resp1 == resp2


# ---------------------------------------------------------------------------
# EventDataLightningStrike – __eq__ (lines 89-91)
# ---------------------------------------------------------------------------


def test_lightning_strike_eq_different_type():
    strike = EventDataLightningStrike(epoch=1, distance_km=10, energy=100)
    assert strike.__eq__("not_a_strike") is NotImplemented


def test_lightning_strike_eq_same():
    s1 = EventDataLightningStrike(epoch=1, distance_km=10, energy=100)
    s2 = EventDataLightningStrike(epoch=1, distance_km=10, energy=100)
    assert s1 == s2


# ---------------------------------------------------------------------------
# EventDataRapidWind – __eq__ (lines 77-79)
# ---------------------------------------------------------------------------


def test_rapid_wind_eq_different_type():
    wind = EventDataRapidWind(
        epoch=1, wind_speed_meters_per_second=3, wind_direction_degrees=90
    )
    assert wind.__eq__(42) is NotImplemented


def test_rapid_wind_eq_same():
    w1 = EventDataRapidWind(
        epoch=1, wind_speed_meters_per_second=3, wind_direction_degrees=90
    )
    w2 = EventDataRapidWind(
        epoch=1, wind_speed_meters_per_second=3, wind_direction_degrees=90
    )
    assert w1 == w2


# ---------------------------------------------------------------------------
# LightningStrikeEventWS – already-converted evt path (line 108->exit)
# ---------------------------------------------------------------------------


def test_lightning_strike_evt_already_converted():
    """When evt is already an EventDataLightningStrike, __post_init__ should not re-convert."""
    strike_data = {
        "type": "evt_strike",
        "device_id": 123,
        "evt": [1710383159, 13, -182],
        "hub_sn": "HB-00061234",
        "serial_number": "ST-00081234",
        "source": "enhanced",
    }
    lse = LightningStrikeEventWS.from_dict(strike_data)
    assert isinstance(lse.evt, EventDataLightningStrike)
    # epoch should be correctly parsed
    assert lse.epoch == 1710383159
    assert lse.distance_km == 13
    assert lse.energy == -182


# ---------------------------------------------------------------------------
# WebsocketResponseBuilder – error paths (lines 208, 212, 218)
# ---------------------------------------------------------------------------


def test_builder_raises_on_missing_type():
    with pytest.raises(ValueError, match="Invalid type"):
        WebsocketResponseBuilder.build_response({"not_type": "something"})


def test_builder_raises_on_unknown_type():
    with pytest.raises(ValueError, match="Invalid type"):
        WebsocketResponseBuilder.build_response({"type": "not_a_real_type"})


def test_builder_returns_none_on_success_status():
    """KeyError with a SUCCESS status_message should return None."""
    data = {
        "type": "ack",
        # 'id' is required for AcknowledgementWS → triggers KeyError
        # but status says SUCCESS
        "status": {"status_message": "SUCCESS"},
    }
    # AcknowledgementWS.from_dict will fail without 'id'; with SUCCESS status → None
    result = WebsocketResponseBuilder.build_response(data)
    assert result is None


def test_builder_raises_on_key_error_without_success():
    """KeyError without a SUCCESS status should re-raise as ValueError."""
    data = {
        "type": "ack",
        # No 'id' field → KeyError during from_dict
        "status": {"status_message": "FAILURE"},
    }
    with pytest.raises(ValueError, match="Invalid response"):
        WebsocketResponseBuilder.build_response(data)
