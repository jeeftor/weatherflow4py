import pytest

from weatherflow4py.models.websocket_response import (
    WebsocketResponseBuilder,
    AcknowledgementWS,
    ConnectionOpenWS,
    ObservationTempestWS,
)
# def test_strange_message():
#
#     json_msg = """
#       {"status":
#         {"status_code":0,"status_message":"SUCCESS"},
#         "device_id":211522,
#         "type":"obs_st",
#         "source":"cache",
#         "summary":{"pressure_trend":"rising","strike_count_1h":0,"strike_count_3h":0,"precip_total_1h":0.0,"strike_last_dist":26,"strike_last_epoch":1707346875,"precip_accum_local_yesterday":0.478541,"precip_accum_local_yesterday_final":1.126487,"precip_analysis_type_yesterday":1,"feels_like":-9.4,"heat_index":-9.4,"wind_chill":-9.4,"raining_minutes":[0,0,0,0,0,0,0,0,0,0,0,0],"dew_point":-10.3,"wet_bulb_temperature":-9.7,"wet_bulb_globe_temperature":-9.2,"air_density":1.04779,"delta_t":0.3,"precip_minutes_local_day":0,"precip_minutes_local_yesterday":22},"obs":[[1709130731,0,0.25,1.09,249,3,793.3,-9.4,93,7987,0.28,67,0,0,0,0,2.62,1,0,0,0,0]]}
#         """
#
#     # This is a rest message not sure what to do with it ....
#     obs_st = DeviceObservationTempestREST.from_dict(json.loads(json_msg))
#


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
