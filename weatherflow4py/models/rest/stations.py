# models/unified_station.py
from __future__ import annotations

from dataclasses import dataclass, field
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
    item: str
    location_id: int
    location_item_id: int
    station_id: int
    station_item_id: int
    sort: Optional[int] = None
    device_id: Optional[int] = field(default=-1)


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

    @property
    def station_map(self) -> dict[int, Stations]:
        """Return a dictionary of stations."""
        return {station.station_id: station for station in self.stations}

    @property
    def station_device_map(self) -> dict[int : list[int]]:
        """Return a dictionary of station_id to list of device_ids."""
        return {
            station.station_id: [device.device_id for device in station.devices]
            for station in self.stations
        }

    @property
    def station_outdoor_device_map(self) -> dict[int : list[int]]:
        """Return a dictionary of station_id to list of outdoor device_ids."""
        return {
            station.station_id: [device.device_id for device in station.outdoor_devices]
            for station in self.stations
        }

    @property
    def device_station_map(self) -> dict[int, int]:
        """Return a dictionary of device_id to station_id."""
        return {
            device.device_id: station.station_id
            for station in self.stations
            for device in station.devices
        }
