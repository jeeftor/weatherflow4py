"""Model for the forecast endpoint."""

from dataclasses import dataclass
from datetime import datetime
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

    @property
    def ha_icon(self) -> str:
        icon_mapping = {
            Icon.CLEAR_DAY: "sunny",
            Icon.CLEAR_NIGHT: "clear-night",
            Icon.CLOUDY: "cloudy",
            Icon.FOGGY: "fog",
            Icon.PARTLY_CLOUDY_DAY: "partlycloudy",
            Icon.PARTLY_CLOUDY_NIGHT: "partlycloudy",
            Icon.POSSIBLY_RAINY_DAY: "pouring",
            Icon.POSSIBLY_RAINY_NIGHT: "pouring",
            Icon.POSSIBLY_SLEET_DAY: "hail",
            Icon.POSSIBLY_SLEET_NIGHT: "hail",
            Icon.POSSIBLY_SNOW_DAY: "snowy",
            Icon.POSSIBLY_SNOW_NIGHT: "snowy",
            Icon.POSSIBLY_THUNDERSTORM_DAY: "lightning-rainy",
            Icon.POSSIBLY_THUNDERSTORM_NIGHT: "lightning-rainy",
            Icon.RAINY: "rainy",
            Icon.SLEET: "hail",
            Icon.SNOW: "snowy",
            Icon.THUNDERSTORM: "lightning",
            Icon.WINDY: "windy-variant",
        }
        return icon_mapping.get(self, "exceptional")


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


@dataclass_json
@dataclass(frozen=True, eq=True)
class CurrentConditions:
    air_density: float
    air_temperature: float
    brightness: int
    conditions: Condition
    delta_t: float  # Added missing field
    dew_point: float
    feels_like: float
    icon: Icon  # Added missing field
    is_precip_local_day_rain_check: bool
    is_precip_local_yesterday_rain_check: bool
    lightning_strike_count_last_1hr: int
    lightning_strike_count_last_3hr: int
    lightning_strike_last_distance: int
    lightning_strike_last_distance_msg: str
    lightning_strike_last_epoch: int
    precip_accum_local_day: int
    precip_accum_local_yesterday: int
    precip_minutes_local_day: int
    precip_minutes_local_yesterday: int
    pressure_trend: PressureTrend
    relative_humidity: int
    sea_level_pressure: float
    solar_radiation: int
    station_pressure: float
    time: int
    uv: int
    wet_bulb_globe_temperature: float
    wet_bulb_temperature: float
    wind_avg: float
    wind_direction: float
    wind_direction_cardinal: WindDirection
    wind_gust: float


@dataclass_json
@dataclass(frozen=True, eq=True)
class ForecastDaily:
    air_temp_high: float
    air_temp_low: float
    conditions: Condition
    day_num: int
    day_start_local: int
    icon: Icon
    month_num: int
    precip_icon: PrecipIcon
    precip_probability: int
    precip_type: PrecipType
    sunrise: int
    sunset: int

    @property
    def rfc3939_datetime(self):
        utc_datetime = datetime.utcfromtimestamp(self.day_start_local)
        return utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def ha_forecast(self) -> dict:
        return {
            "datetime": self.rfc3939_datetime,
            "is_daytime": None,
            "cloud_coverage": None,
            "condition": self.icon.ha_icon,
            "humidity": None,
            "native_apparent_temperature": None,
            "native_dew_point": None,
            "native_precipitation": None,
            "native_pressure": None,
            "native_temperature": self.air_temp_high,
            "native_templow": self.air_temp_high,
            "native_wind_gust_speed": None,
            "native_wind_speed": None,
            "precipitation_probability": self.precip_probability,
            "uv_index": None,
            "wind_bearing": None,
        }


@dataclass_json
@dataclass(frozen=True, eq=True)
class ForecastHourly:
    air_temperature: float
    conditions: Condition
    feels_like: float
    icon: Icon
    local_day: int
    local_hour: int
    precip: int
    precip_probability: int
    precip_type: PrecipType
    relative_humidity: int
    sea_level_pressure: float
    time: int
    uv: float
    wind_avg: float
    wind_direction_cardinal: WindDirection
    wind_direction: float
    wind_gust: float

    @property
    def rfc3939_datetime(self):
        utc_datetime = datetime.utcfromtimestamp(self.time)
        return utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def ha_forecast(self) -> dict:
        """Property for Home Assistant to use"""
        return {
            # UTC Date time in RFC 3339 format.
            "datetime": self.rfc3939_datetime,
            "condition": self.icon.ha_icon,
            "humidity": self.relative_humidity,
            "native_apparent_temperature": self.feels_like,
            "native_precipitation": self.precip,
            "native_temperature": self.air_temperature,
            "native_wind_gust_speed": int(self.wind_gust),
            "native_wind_speed": self.wind_avg,
            "uv_index": self.uv,
            "wind_bearing": self.wind_direction,
        }


@dataclass_json
@dataclass(frozen=True, eq=True)
class Forecast:
    daily: List[ForecastDaily]
    hourly: List[ForecastHourly]


@dataclass_json
@dataclass(frozen=True, eq=True)
class Status:
    status_code: int
    status_message: str


@dataclass_json
@dataclass(frozen=True, eq=True)
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
@dataclass(frozen=True, eq=True)
class WeatherData:
    current_conditions: CurrentConditions
    forecast: Forecast
    latitude: float
    longitude: float
    location_name: str
    timezone: str
    timezone_offset_minutes: int
    units: Units
