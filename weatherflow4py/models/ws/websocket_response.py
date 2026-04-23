"""Websocket Responses.

Documentation form:
 - https://apidocs.tempestwx.com/reference/websocket-reference#lightning-strike-event
 - https://weatherflow.github.io/Tempest/api/ws.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from dataclasses_json import dataclass_json, Undefined, CatchAll

from weatherflow4py.models.rest.device import Summary
from weatherflow4py.models.rest.forecast import WindDirection
from weatherflow4py.models.ws.obs import WebsocketObservation


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class BaseResponseWS:
    type: str
    unknown_fields: CatchAll

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__


@dataclass_json
@dataclass
class AcknowledgementWS(BaseResponseWS):
    id: str


@dataclass_json
@dataclass
class RainStartEventWS(BaseResponseWS):
    device_id: int


@dataclass
class EventDataRapidWind:
    epoch: int
    wind_speed_meters_per_second: int
    wind_direction_degrees: int
    wind_direction_cardinal: WindDirection | None = None

    def __post_init__(self):
        self.wind_direction_cardinal = self._wind_cardinal_direction()

    def _wind_cardinal_direction(self):
        dirs = [
            WindDirection.N,
            WindDirection.NNE,
            WindDirection.NE,
            WindDirection.ENE,
            WindDirection.E,
            WindDirection.ESE,
            WindDirection.SE,
            WindDirection.SSE,
            WindDirection.S,
            WindDirection.SSW,
            WindDirection.SW,
            WindDirection.WSW,
            WindDirection.W,
            WindDirection.WNW,
            WindDirection.NW,
            WindDirection.NNW,
        ]
        ix = round(self.wind_direction_degrees / (360.0 / len(dirs)))
        return dirs[ix % len(dirs)]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__


@dataclass
class EventDataLightningStrike:
    epoch: int
    distance_km: int
    energy: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__


@dataclass_json
@dataclass
class LightningStrikeEventWS(BaseResponseWS):
    """
    Field   Type	    Description
    0	    timestamp	Epoch (seconds, UTC)
    1	    distance	(km)
    2	    energy
    """

    device_id: int
    evt: EventDataLightningStrike | list[Any]

    def __post_init__(self):
        if isinstance(self.evt, list):
            raw: list[Any] = self.evt
            self.evt = EventDataLightningStrike(
                cast(int, raw[0]), cast(int, raw[1]), cast(int, raw[2])
            )

    @property
    def epoch(self) -> int:
        assert isinstance(self.evt, EventDataLightningStrike)
        return self.evt.epoch

    @property
    def distance_km(self) -> int:
        assert isinstance(self.evt, EventDataLightningStrike)
        return self.evt.distance_km

    @property
    def energy(self) -> int:
        assert isinstance(self.evt, EventDataLightningStrike)
        return self.evt.energy


@dataclass_json
@dataclass
class RapidWindWS(BaseResponseWS):
    """
    Rapid Wind stuff.

        Index	Field	        Units
        0	    Time Epoch	    Seconds
        1	    Wind Speed	    m/s
        2	    Wind Direction	Degrees
    """

    device_id: int
    ob: EventDataRapidWind | list[Any]

    def __post_init__(self):
        if isinstance(self.ob, list):
            raw_ob: list[Any] = self.ob
            self.ob = EventDataRapidWind(
                cast(int, raw_ob[0]), cast(int, raw_ob[1]), cast(int, raw_ob[2])
            )


@dataclass_json
@dataclass
class ObservationAirWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary
    source: str
    serial_number: str
    hub_sn: str
    firmware_revision: str


@dataclass_json
@dataclass
class ObservationSkyWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary
    source: str
    serial_number: str
    hub_sn: str
    firmware_revision: str


@dataclass_json
@dataclass
class ObservationTempestWS(BaseResponseWS, WebsocketObservation):
    device_id: int
    summary: Summary
    source: str
    serial_number: str
    hub_sn: str
    firmware_revision: str


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
        if response_type is None:
            raise ValueError(f"Invalid type: {response_type}")
        response_class = type_class_map.get(response_type)

        if response_class is None:
            raise ValueError(f"Invalid type: {response_type}")
        try:
            return cast(Any, response_class).from_dict(data)
        except KeyError as exec:
            if data.get("status", {}).get("status_message") == "SUCCESS":
                return None
            raise ValueError(f"Invalid response: {data}") from exec
