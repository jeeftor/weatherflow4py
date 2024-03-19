# models/unified_station.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json

from weatherflow4py.models.rest.status import Status


@dataclass_json
@dataclass(frozen=True, order=True)
class DeviceMeta:
    agl: float
    environment: str
    name: str
    wifi_network_name: str


@dataclass_json
@dataclass(frozen=True, order=True)
class DeviceSettings:
    show_precip_final: bool


@dataclass_json
@dataclass(frozen=True, order=True)
class Device:
    device_id: int
    device_meta: DeviceMeta
    device_type: str
    firmware_revision: str
    hardware_revision: str
    serial_number: str
    device_settings: Optional[DeviceSettings] = None


@dataclass_json
@dataclass(frozen=True, order=True)
class StationItem:
    device_id: int
    item: str
    location_id: int
    location_item_id: int
    station_id: int
    station_item_id: int
    sort: Optional[int] = None


@dataclass_json
@dataclass(frozen=True, order=True)
class StationMeta:
    elevation: float
    share_with_wf: bool
    share_with_wu: bool


@dataclass_json
@dataclass(frozen=True, order=True)
class Capability:
    capability: str
    device_id: int
    environment: str
    agl: Optional[float] = None
    show_precip_final: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True, order=True)
class Stations:
    created_epoch: int
    devices: list[Device]
    is_local_mode: bool
    last_modified_epoch: int
    latitude: float
    longitude: float
    name: str
    public_name: str
    station_id: int
    station_items: list[StationItem]
    station_meta: StationMeta
    timezone: str
    timezone_offset_minutes: int
    capabilities: list[Capability] | None = None  # Optional field for capabilities

    @property
    def outdoor_devices(self) -> list[Device]:
        """Return a list of outdoor devices."""
        return [d for d in self.devices if d.device_type == "ST"]

    @property
    def indoor_devices(self) -> list[Device]:
        """Return a list of indoor devices."""
        return [d for d in self.devices if d.device_type != "ST"]

    @property
    def elevation(self) -> float:
        return self.station_meta.elevation


@dataclass_json
@dataclass(frozen=True, order=True)
class StationsResponseREST:
    stations: list[Stations]
    status: Status
