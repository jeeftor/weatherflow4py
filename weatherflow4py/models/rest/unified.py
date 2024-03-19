from __future__ import annotations

from dataclasses import dataclass


from weatherflow4py.models.rest.device import DeviceObservationTempestREST
from weatherflow4py.models.rest.forecast import WeatherDataForecastREST
from weatherflow4py.models.rest.observation import ObservationStationREST
from weatherflow4py.models.rest.stations import Stations


@dataclass
class WeatherFlowDataREST:
    """Unified Weather Data Object.

    API suggests to only use station_id Observations in most cases - so we can keep device_observations in general as None
    https://apidocs.tempestwx.com/reference/station-vs-device#should-i-use-a-device-or-a-station-observation
    """

    weather: WeatherDataForecastREST
    station: Stations
    observation: ObservationStationREST
    device_observations: DeviceObservationTempestREST | None

    @property
    def primary_device_id(self) -> int:
        return self.station.outdoor_devices[0].device_id
