"""Websocket Request Messages."""
import json
from abc import ABC, abstractmethod

from weatherflow4py.models.ws.types import LightingStrikeType


class WebsocketRequest(ABC):
    def __init__(self, type: str, id: str):
        self.type = type
        self.id = id

    @abstractmethod
    def to_dict(self):
        pass

    @property
    def json(self) -> str:
        return json.dumps(self.to_dict())


class ListenStartMessage(WebsocketRequest):
    def __init__(self, device_id: str):
        super().__init__("listen_start", "2098388936")
        self.device_id = device_id

    def to_dict(self):
        return {"type": self.type, "device_id": self.device_id, "id": self.id}


class ListenStopMessage(WebsocketRequest):
    def __init__(self, device_id: str):
        super().__init__("listen_stop", "2098388936")
        self.device_id = device_id

    def to_dict(self):
        return {"type": self.type, "device_id": self.device_id, "id": self.id}


class GeoStrikeListenStartMessage(WebsocketRequest):
    def __init__(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        strike_type: LightingStrikeType = None,
    ):
        super().__init__("geo_strike_listen_start", "whatever")
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.strike_type = strike_type

    def to_dict(self):
        message_dict = {
            "type": self.type,
            "lat_min": self.lat_min,
            "lat_max": self.lat_max,
            "lon_min": self.lon_min,
            "lon_max": self.lon_max,
            "id": self.id,
        }
        if self.strike_type is not None:
            message_dict["strike_type"] = self.strike_type
        return message_dict


class RapidWindListenStartMessage(WebsocketRequest):
    def __init__(self, device_id: str):
        super().__init__("listen_rapid_start", "2098388542")
        self.device_id = device_id

    def to_dict(self):
        return {"type": self.type, "device_id": self.device_id, "id": self.id}


class RapidWindListenStopMessage(WebsocketRequest):
    def __init__(self, device_id: str):
        super().__init__("listen_rapid_stop", "2098388587")
        self.device_id = device_id

    def to_dict(self):
        return {"type": self.type, "device_id": self.device_id, "id": self.id}
