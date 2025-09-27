import pytest

from weatherflow4py.models.ws.websocket_request import (
    GeoStrikeListenStartMessage,
    LightingStrikeType,
)
from weatherflow4py.models.ws.websocket_response import (
    WebsocketResponseBuilder,
    AcknowledgementWS,
    ConnectionOpenWS,
    ObservationTempestWS,
    RapidWindWS,
    EventDataRapidWind,
    LightningStrikeEventWS,
)


def test_ws_strike(websocket_strike):
    lse: LightningStrikeEventWS = LightningStrikeEventWS.from_dict(websocket_strike)
    assert lse.unknown_fields == {
        "hub_sn": "HB-00061234",
        "serial_number": "ST-00081234",
        "source": "enhanced",
    }

    assert lse.energy == -182
    assert lse.epoch == 1710383159
    assert lse.distance_km == 13


def test_websocket_messages(websocket_messages):
    msg0 = WebsocketResponseBuilder.build_response(websocket_messages[0])
    assert isinstance(msg0, ConnectionOpenWS)
    msg1 = WebsocketResponseBuilder.build_response(websocket_messages[1])
    assert isinstance(msg1, AcknowledgementWS)

    with pytest.raises(Exception) as exc_info:
        WebsocketResponseBuilder.build_response(websocket_messages[2])
        assert exc_info is ValueError
        assert exc_info.type == "Taco"
        assert "An error occurred" in str(exc_info.value)
        print(exc_info)

    msg3 = WebsocketResponseBuilder.build_response(websocket_messages[3])
    assert isinstance(msg3, ObservationTempestWS)
    msg4 = WebsocketResponseBuilder.build_response(websocket_messages[4])
    assert isinstance(msg4, ObservationTempestWS)
    msg5 = WebsocketResponseBuilder.build_response(websocket_messages[5])
    assert isinstance(msg5, ObservationTempestWS)
    msg6 = WebsocketResponseBuilder.build_response(websocket_messages[6])
    assert isinstance(msg6, ObservationTempestWS)

    assert msg3.device_id == 211522
    assert msg3.epoch == 1709130791

    assert msg6.summary.strike_last_dist == None
    assert msg6.summary.strike_last_epoch == None

def test_winds(websocket_winds):
    for msg in websocket_winds:
        wind = WebsocketResponseBuilder.build_response(msg)
        assert isinstance(wind, RapidWindWS)
        assert isinstance(wind.ob, EventDataRapidWind)


@pytest.mark.parametrize(
    "strike_type, expected",
    [
        (LightingStrikeType.ALL, "all"),
        (LightingStrikeType.CLOUD_TO_GROUND, "cg"),
        (LightingStrikeType.CLOUD_TO_CLOUD, "ic"),
        (None, None),
    ],
)
def test_geo_strike_listen_start_message_to_dict_with_different_strike_types(
    strike_type, expected
):
    message = GeoStrikeListenStartMessage(
        lat_min=37.28,
        lat_max=41.32,
        lon_min=-101.76,
        lon_max=-91.00,
        strike_type=strike_type,
    )
    message_dict = message.to_dict()
    assert message_dict["type"] == "geo_strike_listen_start"
    assert message_dict["lat_min"] == 37.28
    assert message_dict["lat_max"] == 41.32
    assert message_dict["lon_min"] == -101.76
    assert message_dict["lon_max"] == -91.00
    assert "id" in message_dict
    if expected is not None:
        assert message_dict["strike_type"] == expected
    else:
        assert "strike_type" not in message_dict
