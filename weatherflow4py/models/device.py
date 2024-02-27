from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json
from typing import List, Union


class DeviceObservationType(Enum):
    AIR = "obs_air"
    SKY = "obs_sky"
    STATION = "obs_st"


class ObservationPrecipitationType(Enum):
    """(0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))"""

    NONE = 0
    RAIN = 1
    HAIL = 2
    RAIN_AND_HAIL = 3


class ObservationPrecipitationAnalysisType(Enum):
    """0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user display off"""

    NONE = 0
    RAIN_CHECK_WITH_USER_DISPLAY_ON = 1
    RAIN_CHECK_WITH_USER_DISPLAY_OFF = 2


@dataclass_json
@dataclass
class Status:
    status_code: int
    status_message: str


@dataclass_json
@dataclass
class Summary:
    pressure_trend: str
    strike_count_1h: int
    strike_count_3h: int
    precip_total_1h: float
    strike_last_dist: int
    strike_last_epoch: int
    precip_accum_local_yesterday: float
    precip_accum_local_yesterday_final: float
    precip_analysis_type_yesterday: ObservationPrecipitationAnalysisType
    feels_like: float
    heat_index: float
    wind_chill: float


@dataclass_json
@dataclass
class DeviceObservation:
    status: Status
    device_id: int
    type: DeviceObservationType
    source: str
    summary: Summary
    obs: List[List[Union[float, int]]]

    @property
    def epoch(self) -> int:
        return self.obs[0][0]


@dataclass_json
@dataclass
class DeviceObservationTempest(DeviceObservation):
    """Define the specific properties of a Tempest observation"""

    @property
    def wind_lull(self) -> float:
        """Wind Lull in m/s"""
        return self.obs[0][1]

    @property
    def wind_avg(self) -> float:
        """Wind Average in m/s"""
        return self.obs[0][2]

    @property
    def wind_gust(self) -> float:
        """Wind Gust in m/s"""
        return self.obs[0][3]

    @property
    def wind_direction(self) -> int:
        """Wind Direction in degrees"""
        return self.obs[0][4]

    @property
    def wind_sample_interval(self) -> int:
        """Wind Sample Interval in seconds"""
        return self.obs[0][5]

    @property
    def pressure(self) -> float:
        """Pressure in MB"""
        return self.obs[0][6]

    @property
    def air_temperature(self) -> float:
        """Air Temperature in Celsius"""
        return self.obs[0][7]

    @property
    def relative_humidity(self) -> int:
        """Relative Humidity in percentage"""
        return self.obs[0][8]

    @property
    def illuminance(self) -> int:
        """Illuminance in lux"""
        return self.obs[0][9]

    @property
    def uv(self) -> float:
        """UV index"""
        return self.obs[0][10]

    @property
    def solar_radiation(self) -> float:
        """Solar Radiation in W/m^2"""
        return self.obs[0][11]

    @property
    def rain_accumulation(self) -> float:
        """Rain Accumulation in mm"""
        return self.obs[0][12]

    @property
    def precipitation_type(self) -> ObservationPrecipitationType:
        """Precipitation Type (0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))"""
        return ObservationPrecipitationType(self.obs[0][13])

    @property
    def average_strike_distance(self) -> float:
        """Average Strike Distance in km"""
        return self.obs[0][14]

    @property
    def strike_count(self) -> int:
        """Strike Count"""
        return self.obs[0][15]

    @property
    def battery(self) -> float:
        """Battery in volts"""
        return self.obs[0][16]

    @property
    def report_interval(self) -> int:
        """Report Interval in minutes"""
        return self.obs[0][17]

    @property
    def local_day_rain_accumulation(self) -> float:
        """Local Day Rain Accumulation in mm"""
        return self.obs[0][18]

    @property
    def nc_rain_accumulation(self) -> float:
        """NC Rain Accumulation in mm"""
        return self.obs[0][19]

    @property
    def local_day_nc_rain_accumulation(self) -> float:
        """Local Day NC Rain Accumulation in mm"""
        return self.obs[0][20]

    @property
    def precipitation_analysis_type(self) -> ObservationPrecipitationAnalysisType:
        """Precipitation Analysis Type (0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user
        display off)"""
        return ObservationPrecipitationAnalysisType(self.obs[0][21])


@dataclass_json
@dataclass
class DeviceObservationAir(DeviceObservation):
    """Define the specific properties of a station observation"""

    @property
    def station_pressure(self) -> float:
        """Station Pressure in MB"""
        return self.obs[0][1]

    @property
    def air_temperature(self) -> float:
        """Air Temperature in Celsius"""
        return self.obs[0][2]

    @property
    def relative_humidity(self) -> int:
        """Relative Humidity in percentage"""
        return self.obs[0][3]

    @property
    def lightning_strike_count(self) -> int:
        """Lightning Strike Count"""
        return self.obs[0][4]

    @property
    def lightning_strike_average_distance(self) -> float:
        """Lightning Strike Average Distance in km"""
        return self.obs[0][5]

    @property
    def battery(self) -> float:
        """Battery in volts"""
        return self.obs[0][6]

    @property
    def report_interval(self) -> int:
        """Report Interval in minutes"""
        return self.obs[0][7]


@dataclass
class DeviceObservationSky(DeviceObservation):
    """Define the specific properties of a sky observation"""

    @property
    def epoch(self) -> int:
        """Epoch in seconds UTC"""
        return self.obs[0][0]

    @property
    def illuminance(self) -> int:
        """Illuminance in lux"""
        return self.obs[0][1]

    @property
    def uv(self) -> float:
        """UV index"""
        return self.obs[0][2]

    @property
    def rain_accumulation(self) -> float:
        """Rain Accumulation in mm"""
        return self.obs[0][3]

    @property
    def wind_lull(self) -> float:
        """Wind Lull in m/s"""
        return self.obs[0][4]

    @property
    def wind_avg(self) -> float:
        """Wind Average in m/s"""
        return self.obs[0][5]

    @property
    def wind_gust(self) -> float:
        """Wind Gust in m/s"""
        return self.obs[0][6]

    @property
    def wind_direction(self) -> int:
        """Wind Direction in degrees"""
        return self.obs[0][7]

    @property
    def battery(self) -> float:
        """Battery in volts"""
        return self.obs[0][8]

    @property
    def report_interval(self) -> int:
        """Report Interval in minutes"""
        return self.obs[0][9]

    @property
    def solar_radiation(self) -> float:
        """Solar Radiation in W/m^2"""
        return self.obs[0][10]

    @property
    def local_day_rain_accumulation(self) -> float:
        """Local Day Rain Accumulation in mm"""
        return self.obs[0][11]

    @property
    def precipitation_type(self) -> ObservationPrecipitationType:
        """Precipitation Type (0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))"""
        return ObservationPrecipitationType(self.obs[0][12])

    @property
    def wind_sample_interval(self) -> int:
        """Wind Sample Interval in seconds"""
        return self.obs[0][13]

    @property
    def nc_rain(self) -> float:
        """NC Rain in mm"""
        return self.obs[0][14]

    @property
    def local_day_nc_rain_accumulation(self) -> float:
        """Local Day NC Rain Accumulation in mm"""
        return self.obs[0][15]

    @property
    def precipitation_analysis_type(self) -> ObservationPrecipitationAnalysisType:
        """Precipitation Analysis Type (0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user
        display off)"""
        return ObservationPrecipitationAnalysisType(self.obs[0][16])
