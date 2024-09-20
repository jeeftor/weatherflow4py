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
    SNOW_LIKELY = "Snow Likely"
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
    LIGHT_RAIN = "Light Rain"
    MODERATE_RAIN = "Moderate Rain"
    HEAVY_RAIN = "Heavy Rain"
    VERY_HEAVY_RAIN = "Very Heavy Rain"
    EXTREME_RAIN = "Extreme Rain"


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
    def emoji(self) -> str:
        icon_mapping = {
            Icon.CLEAR_DAY: "☀️",
            Icon.CLEAR_NIGHT: "🌌️",
            Icon.CLOUDY: "☁️",
            Icon.FOGGY: "🌫️",
            Icon.PARTLY_CLOUDY_DAY: "⛅️",
            Icon.PARTLY_CLOUDY_NIGHT: "☁️",
            Icon.POSSIBLY_RAINY_DAY: "🌧️",
            Icon.POSSIBLY_RAINY_NIGHT: "🌧️",
            Icon.POSSIBLY_SLEET_DAY: "🌨️",
            Icon.POSSIBLY_SLEET_NIGHT: "🌨️",
            Icon.POSSIBLY_SNOW_DAY: "❄️",
            Icon.POSSIBLY_SNOW_NIGHT: "❄️",
            Icon.POSSIBLY_THUNDERSTORM_DAY: "⛈️",
            Icon.POSSIBLY_THUNDERSTORM_NIGHT: "⛈️",
            Icon.RAINY: "🌧️",
            Icon.SLEET: "🌨️",
            Icon.SNOW: "❄️️",
            Icon.THUNDERSTORM: "⛈️",
            Icon.WINDY: "💨️",
        }
        return icon_mapping.get(self, "❓️")

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
    NONE = "none"


class PrecipIcon(Enum):
    CHANCE_RAIN = "chance-rain"
    CHANCE_SNOW = "chance-snow"
    CHANCE_SLEET = "chance-sleet"
    NONE = "none"


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


@dataclass_json()
@dataclass(frozen=True, eq=True)
class CurrentConditions:
    air_temperature: float
    conditions: Condition

    feels_like: float
    icon: Icon  # Added missing field
    is_precip_local_day_rain_check: bool

    pressure_trend: PressureTrend
    relative_humidity: int
    sea_level_pressure: float
    solar_radiation: int
    time: int
    uv: int
    wet_bulb_globe_temperature: float
    wet_bulb_temperature: float
    wind_avg: float
    wind_direction: float
    wind_direction_cardinal: WindDirection
    wind_gust: float

    brightness: int | None = None
    station_pressure: float | None = None
    delta_t: float | None = None
    dew_point: float | None = None
    lightning_strike_count_last_1hr: int = 0
    lightning_strike_count_last_3hr: int = 0
    lightning_strike_last_distance: int = 0
    lightning_strike_last_distance_msg: str = ""
    lightning_strike_last_epoch: int | None = None
    precip_accum_local_day: int | None = None
    precip_accum_local_yesterday: int | None = None
    precip_minutes_local_day: int | None = None
    precip_minutes_local_yesterday: int | None = None
    air_density: float | None = None
    is_precip_local_yesterday_rain_check: bool | None = None


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
    precip_probability: int
    sunrise: int
    sunset: int

    precip_icon: PrecipIcon = PrecipIcon.NONE
    precip_type: PrecipType = PrecipType.NONE

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
            "native_templow": self.air_temp_low,
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
    icon: Icon
    local_day: int
    local_hour: int
    precip: int
    precip_probability: int
    precip_type: PrecipType
    relative_humidity: int
    sea_level_pressure: float
    time: int
    wind_avg: float
    wind_direction_cardinal: WindDirection
    wind_direction: float
    wind_gust: float
    feels_like: float | None = None
    uv: float | None = None

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
            "native_pressure": self.sea_level_pressure,
            "native_temperature": self.air_temperature,
            "native_wind_gust_speed": int(self.wind_gust),
            "native_wind_speed": self.wind_avg,
            "precipitation_probability": self.precip_probability,
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
class ForecastUnits:
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
class WeatherDataForecastREST:
    current_conditions: CurrentConditions
    forecast: Forecast
    latitude: float
    longitude: float
    location_name: str
    timezone: str
    timezone_offset_minutes: int
    units: ForecastUnits
