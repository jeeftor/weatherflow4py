"""Model for the forecast endpoint."""

from dataclasses import dataclass
from typing import List
from dataclasses_json import dataclass_json
from enum import Enum


class Condition(Enum):
    CLEAR = "Clear"
    RAIN_LIKELY = "Rain Likely"
    RAIN_POSSIBLE = "Rain Possible"
    SNOW = "Snow"
    SNOW_POSSIBLE = "Snow Possible"
    WINTRY_MIX_LIKELY = "Wintry Mix Likely"
    WINTRY_MIX_POSSIBLE = "Wintry Mix Possible"
    THUNDERSTORMS_LIKELY = "Thunderstorms Likely"
    THUNDERSTORMS_POSSIBLE = "Thunderstorms Possible"
    WINDY = "Windy"
    FOGGY = "Foggy"
    CLOUDY = "Cloudy"
    PARTLY_CLOUDY = "Partly Cloudy"
    VERY_LIGHT_RAIN = "Very Light Rain"


class Icon(Enum):
    CLEAR_DAY = "clear-day"
    CLEAR_NIGHT = "clear-night"
    CLOUDY = "cloudy"
    FOGGY = "foggy"
    PARTLY_CLOUDY_DAY = "partly-cloudy-day"
    PARTLY_CLOUDY_NIGHT = "partly-cloudy-night"
    POSSIBLY_RAINY_DAY = "possibly-rainy-day"
    POSSIBLY_RAINY_NIGHT = "possibly-rainy-night"
    POSSIBLY_SLEET_DAY = "possibly-sleet-day"
    POSSIBLY_SLEET_NIGHT = "possibly-sleet-night"
    POSSIBLY_SNOW_DAY = "possibly-snow-day"
    POSSIBLY_SNOW_NIGHT = "possibly-snow-night"
    POSSIBLY_THUNDERSTORM_DAY = "possibly-thunderstorm-day"
    POSSIBLY_THUNDERSTORM_NIGHT = "possibly-thunderstorm-night"
    RAINY = "rainy"
    SLEET = "sleet"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    WINDY = "windy"


class PrecipType(Enum):
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"
    STORM = "storm"


class PrecipIcon(Enum):
    CHANCE_RAIN = "chance-rain"
    CHANCE_SNOW = "chance-snow"
    CHANCE_SLEET = "chance-sleet"


class PressureTrend(Enum):
    FALLING = "falling"
    STEADY = "steady"
    RISING = "rising"
    UNKNOWN = "unknown"


class WindDirection(Enum):
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"


class TemperatureUnit(Enum):
    CELSIUS = "C"
    FAHRENHEIT = "F"


class WindSpeedUnit(Enum):
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"


class VisibilityUnit(Enum):
    KILOMETERS = "km"
    MILES = "mi"


class CurrentConditions:
    air_density: float
    air_temperature: float
    brightness: int
    conditions: Condition
    dew_point: float
    feels_like: float
    pressure_trend: PressureTrend
    relative_humidity: int
    sea_level_pressure: float
    solar_radiation: int
    station_pressure: float
    time: int
    uv: int
    wind_avg: float
    wind_direction: float
    wind_direction_cardinal: WindDirection
    wind_gust: float


@dataclass_json
@dataclass
class ForecastDaily:
    air_temp_high: float
    air_temp_low: float
    conditions: Condition
    day_num: int
    icon: Icon
    month_num: int
    precip_icon: PrecipIcon
    precip_probability: int
    precip_type: PrecipType
    sunrise: int
    sunset: int


@dataclass_json
@dataclass
class ForecastHourly:
    air_temperature: float
    conditions: Condition
    feels_like: float
    icon: Icon
    local_day: int
    local_hour: int
    precip: int
    precip_type: PrecipType
    relative_humidity: int
    time: int
    uv: float
    wind_avg: float
    wind_direction_cardinal: WindDirection
    wind_direction: float


@dataclass_json
@dataclass
class Forecast:
    daily: List[ForecastDaily]
    hourly: List[ForecastHourly]


@dataclass_json
@dataclass
class Status:
    status_code: int
    status_message: str


@dataclass_json
@dataclass
class Units:
    units_air_density: str
    units_brightness: str
    units_distance: str
    units_other: str
    units_precip: str
    units_pressure: str
    units_solar_radiation: str
    units_temp: str
    units_wind: str


@dataclass_json
@dataclass
class WeatherData:
    current_conditions: CurrentConditions
    forecast: Forecast
    latitude: float
    longitude: float
    location_name: str
    timezone: str
    timezone_offset_minutes: int
    units: Units
