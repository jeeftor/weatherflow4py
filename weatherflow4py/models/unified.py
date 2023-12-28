from dataclasses import dataclass

from weatherflow4py.models.forecast import WeatherData
from weatherflow4py.models.station import Station


@dataclass
class WeatherFlowData:
    weather: WeatherData
    station: Station
