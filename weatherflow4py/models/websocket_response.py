from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from weatherflow4py.models.device import Summary
from weatherflow4py.models.obs import WebsocketObservation


@dataclass_json
@dataclass
class BaseResponseWS:
    type: str


@dataclass_json
@dataclass
class AcknowledgementWS(BaseResponseWS):
    id: str


@dataclass_json
@dataclass
class RainStartEventWS(BaseResponseWS):
    device_id: int


@dataclass_json
@dataclass
class LightningStrikeEventWS(BaseResponseWS):
    device_id: int
    evt: List[int]


@dataclass_json
@dataclass
class RapidWindWS(BaseResponseWS):
    device_id: int
    ob: List[int]


@dataclass_json
@dataclass
class ObservationAirWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary


@dataclass_json
@dataclass
class ObservationSkyWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary


@dataclass_json
@dataclass
class ObservationTempestWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary


@dataclass_json
@dataclass
class ConnectionOpenWS(BaseResponseWS):
    pass


class WebsocketResponseBuilder:
    @staticmethod
    def build_response(data: dict):
        type_class_map = {
            "ack": AcknowledgementWS,
            "evt_precip": RainStartEventWS,
            "evt_strike": LightningStrikeEventWS,
            "rapid_wind": RapidWindWS,
            "obs_air": ObservationAirWS,
            "obs_sky": ObservationSkyWS,
            "obs_st": ObservationTempestWS,
            "connection_opened": ConnectionOpenWS,
        }

        response_type = data.get("type")
        response_class = type_class_map.get(response_type)

        if response_class is None:
            raise ValueError(f"Invalid type: {response_type}")
        try:
            return response_class.from_dict(data)
        except KeyError as exec:
            raise ValueError(f"Invalid response: {data}") from exec
