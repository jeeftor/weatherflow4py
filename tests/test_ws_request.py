from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage,
    ListenStopMessage,
    GeoStrikeListenStartMessage,
    RapidWindListenStartMessage,
    RapidWindListenStopMessage,
    LightingStrikeType,
)


def test_listen_start_message_to_dict():
    message = ListenStartMessage(device_id="1110")
    message_dict = message.to_dict()
    assert message_dict["type"] == "listen_start"
    assert message_dict["device_id"] == "1110"
    assert "id" in message_dict


def test_listen_stop_message_to_dict():
    message = ListenStopMessage(device_id="1110")
    message_dict = message.to_dict()
    assert message_dict["type"] == "listen_stop"
    assert message_dict["device_id"] == "1110"
    assert "id" in message_dict


def test_geo_strike_listen_start_message_to_dict_without_strike_type():
    message = GeoStrikeListenStartMessage(
        lat_min=37.28, lat_max=41.32, lon_min=-101.76, lon_max=-91.00
    )
    message_dict = message.to_dict()
    assert message_dict["type"] == "geo_strike_listen_start"
    assert message_dict["lat_min"] == 37.28
    assert message_dict["lat_max"] == 41.32
    assert message_dict["lon_min"] == -101.76
    assert message_dict["lon_max"] == -91.00
    assert "id" in message_dict
    assert "strike_type" not in message_dict


def test_geo_strike_listen_start_message_to_dict_with_strike_type():
    message = GeoStrikeListenStartMessage(
        lat_min=37.28,
        lat_max=41.32,
        lon_min=-101.76,
        lon_max=-91.00,
        strike_type=LightingStrikeType.ALL,
    )
    message_dict = message.to_dict()
    assert message_dict["type"] == "geo_strike_listen_start"
    assert message_dict["lat_min"] == 37.28
    assert message_dict["lat_max"] == 41.32
    assert message_dict["lon_min"] == -101.76
    assert message_dict["lon_max"] == -91.00
    assert "id" in message_dict
    assert message_dict["strike_type"] == "all"


def test_listen_rapid_start_message_to_dict():
    message = RapidWindListenStartMessage(device_id="1110")
    message_dict = message.to_dict()
    assert message_dict["type"] == "listen_rapid_start"
    assert message_dict["device_id"] == "1110"
    assert "id" in message_dict


def test_listen_rapid_stop_message_to_dict():
    message = RapidWindListenStopMessage(device_id="1110")
    message_dict = message.to_dict()
    assert message_dict["type"] == "listen_rapid_stop"
    assert message_dict["device_id"] == "1110"
    assert "id" in message_dict
