from dataclasses import dataclass

from weatherflow4py.models.device import DeviceObservationTempestREST
from weatherflow4py.models.forecast import WeatherData
from weatherflow4py.models.observation import StationObservation
from weatherflow4py.models.station import Station


@dataclass
class WeatherFlowData:
    """Unified Weather Data Object.."""

    weather: WeatherData
    station: Station
    observation: StationObservation
    device_observations: DeviceObservationTempestREST | None
