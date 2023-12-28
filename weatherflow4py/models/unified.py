from dataclasses import dataclass

from weatherflow4py.models.forecast import WeatherData
from weatherflow4py.models.station import Station


@dataclass
class WeatherFlowData:
    """I couldn't get the data classes to hash so I made a unified class to use."""
    weather: WeatherData
    station: Station
