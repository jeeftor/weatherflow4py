# models/unified_station.py

from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DeviceMeta:
    agl: float
    environment: str
    name: str
    wifi_network_name: str


@dataclass_json
@dataclass
class DeviceSettings:
    show_precip_final: bool


@dataclass_json
@dataclass
class Device:
    device_id: int
    device_meta: DeviceMeta
    device_type: str
    firmware_revision: str
    hardware_revision: str
    serial_number: str
    device_settings: Optional[DeviceSettings] = None


@dataclass_json
@dataclass
class StationItem:
    device_id: int
    item: str
    location_id: int
    location_item_id: int
    station_id: int
    station_item_id: int
    sort: Optional[int] = None


@dataclass_json
@dataclass
class StationMeta:
    elevation: float
    share_with_wf: bool
    share_with_wu: bool


@dataclass_json
@dataclass
class Capability:
    capability: str
    device_id: int
    environment: str
    agl: Optional[float] = None
    show_precip_final: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True)
class Station:
    created_epoch: int
    devices: List[Device]
    is_local_mode: bool
    last_modified_epoch: int
    latitude: float
    longitude: float
    name: str
    public_name: str
    station_id: int
    station_items: List[StationItem]
    station_meta: StationMeta
    timezone: str
    timezone_offset_minutes: int
    capabilities: Optional[List[Capability]] = None  # Optional field for capabilities

    @property
    def elevation(self) -> float:
        return self.station_meta.elevation


@dataclass_json
@dataclass
class Status:
    status_code: int
    status_message: str


@dataclass_json
@dataclass
class StationsResponse:
    stations: List[Station]
    status: Status
