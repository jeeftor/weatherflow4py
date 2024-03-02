from dataclasses import dataclass

from weatherflow4py.models.device import DeviceObservationTempestREST
from weatherflow4py.models.rest_betterforecast import WeatherData
from weatherflow4py.models.observation import StationObservation
from weatherflow4py.models.rest_station import Station


@dataclass
class WeatherFlowData:
    """Unified Weather Data Object.."""

    weather: WeatherData
    station: Station
    observation: StationObservation
    device_observations: DeviceObservationTempestREST | None
