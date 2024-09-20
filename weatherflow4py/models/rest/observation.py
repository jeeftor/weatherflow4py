from dataclasses import dataclass, field
from enum import Enum
from typing import List
from dataclasses_json import dataclass_json, Undefined, CatchAll

from weatherflow4py.const import BASE_LOGGER
from weatherflow4py.models.rest.forecast import WindDirection


class WetBulbFlag(Enum):
    NONE = 0
    WHITE = 1
    GREEN = 2
    YELLOW = 3
    RED = 4
    BLACK = 5


@dataclass_json
@dataclass(frozen=True, eq=True)
class Observation:
    air_temperature: float

    brightness: int

    dew_point: float
    feels_like: float
    heat_index: float

    precip: float
    pressure_trend: str
    relative_humidity: int

    solar_radiation: int

    timestamp: int
    uv: float

    wind_avg: float
    wind_chill: float
    wind_direction: int
    wind_gust: float
    wind_lull: float

    # Optional Fields Discovered June 18
    air_density: float | None = None
    barometric_pressure: float | None = None
    delta_t: float | None = None
    sea_level_pressure: float | None = None
    station_pressure: float | None = None
    wet_bulb_globe_temperature: float | None = None
    wet_bulb_temperature: float | None = None

    # Potentially optional fields based on test data - this may grow over time.
    precip_accum_last_1hr: float = field(default=0.0)
    precip_accum_local_day: float = field(default=0.0)
    precip_accum_local_day_final: float = field(default=0.0)
    precip_accum_local_yesterday: float = field(default=0.0)
    precip_accum_local_yesterday_final: float = field(default=0.0)
    precip_analysis_type_yesterday: int = field(default=0)
    precip_minutes_local_day: int = field(default=0)
    precip_minutes_local_yesterday: int = field(default=0)
    precip_minutes_local_yesterday_final: int = field(default=0)

    lightning_strike_count: int = field(default=0)
    lightning_strike_count_last_1hr: int = field(default=0)
    lightning_strike_count_last_3hr: int = field(default=0)
    lightning_strike_last_distance: int = field(default=0)
    lightning_strike_last_epoch: int | None = field(default=None)

    @property
    def precip_accum_local_day_nearcast(self) -> float:
        """Alias for nearcast"""
        return self.precip_accum_local_day_final

    @property
    def precip_accum_local_yesterday_nearcast(self) -> float:
        """Alias for nearcast"""
        return self.precip_accum_local_yesterday_final

    @property
    def precip_minutes_local_yesterday_nearcast(self) -> float:
        """Alias for nearcast"""
        return self.precip_minutes_local_yesterday_final

    @property
    def wind_cardinal_direction(self) -> str:
        dirs = [
            WindDirection.N,
            WindDirection.NNE,
            WindDirection.NE,
            WindDirection.ENE,
            WindDirection.E,
            WindDirection.ESE,
            WindDirection.SE,
            WindDirection.SSE,
            WindDirection.S,
            WindDirection.SSW,
            WindDirection.SW,
            WindDirection.WSW,
            WindDirection.W,
            WindDirection.WNW,
            WindDirection.NW,
            WindDirection.NNW,
        ]
        ix = round(self.wind_direction / (360.0 / len(dirs)))
        return dirs[ix % len(dirs)].value

    @property
    def wet_bulb_globe_temperature_category(self) -> int:
        """Calculates a wet bulb globe temp category - based on wikipedia:
        https://en.wikipedia.org/wiki/Wet-bulb_globe_temperature."""
        if self.wet_bulb_globe_temperature <= 25.6:
            return 0  # No Risk
        if self.wet_bulb_globe_temperature <= 27.7:
            return 1  # Low risk
        if self.wet_bulb_globe_temperature <= 29.4:
            return 2  # Moderate risk
        if self.wet_bulb_globe_temperature <= 31.0:
            return 3
        if self.wet_bulb_globe_temperature <= 32.1:
            return 4
        return 5

    @property
    def wet_bulb_globe_temperature_flag(self) -> WetBulbFlag:
        return WetBulbFlag(self.wet_bulb_globe_temperature_category)

    @property
    def uv_index_color(self) -> str:
        """Return the UV index color."""
        if self.uv <= 2:
            return "green"
        if self.uv <= 5:
            return "yellow"
        if self.uv <= 7:
            return "orange"
        if self.uv <= 10:
            return "red"
        return "purple"

    @property
    def uv_index_exposure(self) -> str:
        """Return the UV exposure level."""
        if self.uv <= 2:
            return "low"
        if self.uv <= 5:
            return "moderate"
        if self.uv <= 7:
            return "high"
        if self.uv <= 10:
            return "very high"
        return "extreme"


@dataclass_json
@dataclass(frozen=True, eq=True)
class StationUnits:
    """The station_units values represent the units of the Station's owner, not the units of the observation values
    in the API response."""

    units_temp: str
    units_wind: str
    units_precip: str
    units_pressure: str
    units_distance: str
    units_direction: str
    units_other: str


@dataclass_json
@dataclass(frozen=True, eq=True)
class StationStatus:
    status_code: int
    status_message: str

    def __post_init__(self):
        if (
            self.status_message
            == "SUCCESS - Either no capabilities or no recent observations"
        ):
            BASE_LOGGER.debug(
                "No Capabilities or Recent Observations - Station may be offline"
            )


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass(frozen=True, eq=True)
class ObservationStationREST:
    """Top level field for both the observations/device/device_id and observations/station/station_id endpoints."""

    elevation: float
    is_public: bool
    latitude: float
    longitude: float
    obs: List[Observation]
    outdoor_keys: List[str]
    public_name: str
    station_id: int
    station_name: str
    station_units: StationUnits
    status: StationStatus
    timezone: str
    unknown_fields: CatchAll
