import pytest

from weatherflow4py.models.websocket_response import (
    WebsocketResponseBuilder,
    AcknowledgementWS,
    ConnectionOpenWS,
    ObservationTempestWS,
    RapidWindWS,
    EventDataRapidWind,
)


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

    assert msg3.device_id == 211522
    assert msg3.epoch == 1709130791


def test_winds(websocket_winds):
    for msg in websocket_winds:
        wind = WebsocketResponseBuilder.build_response(msg)
        assert isinstance(wind, RapidWindWS)
        assert isinstance(wind.ob, EventDataRapidWind)
