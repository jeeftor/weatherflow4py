from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TempestRequest:
    device_id: str
    id: str
    type: str = None  # Will be set by subclasses


class ListenStart(TempestRequest):
    type = "listen_start"


class ListenStop(TempestRequest):
    type = "listen_stop"


class RapidWindStart(TempestRequest):
    type = "rapid_wind_start"


class RapidWindStop(TempestRequest):
    type = "rapid_wind_stop"
