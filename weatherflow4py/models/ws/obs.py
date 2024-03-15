"""Base message types for websockets."""
from dataclasses import dataclass
from typing import List, Union, Any, Type

from weatherflow4py.models.ws.custom_types import (
    PrecipitationAnalysisType,
    ObservationType,
    PrecipitationType,
)


@dataclass
class base_obs:
    """Base observation class with a class method for creating instances from lists."""

    @classmethod
    def from_list(cls: Type["base_obs"], lst: List) -> "base_obs":
        return cls(*lst)


# Define the base observation classes with a class method for creating instances from lists
@dataclass
class obs_sky(base_obs):
    """Dataclass for the sky observation type."""

    epoch: int
    illuminance: int
    uv: float
    rain_accumulation: float
    wind_lull: float
    wind_avg: float
    wind_gust: float
    wind_direction: int
    battery: float
    report_interval: int
    solar_radiation: float
    local_day_rain_accumulation: float
    precipitation_type: PrecipitationType
    wind_sample_interval: int
    nc_rain: float
    local_day_nc_rain_accumulation: float
    precipitation_analysis_type: PrecipitationAnalysisType


@dataclass
class obs_st(base_obs):
    """Dataclass for the station_id observation type."""

    epoch: int
    wind_lull: float
    wind_avg: float
    wind_gust: float
    wind_direction: int
    wind_sample_interval: int
    pressure: float
    air_temperature: float
    relative_humidity: int
    illuminance: int
    uv: float
    solar_radiation: float
    rain_accumulation: float
    precipitation_type: PrecipitationType
    average_strike_distance: int
    strike_count: int
    battery: float
    report_interval: int
    local_day_rain_accumulation: float
    nc_rain_accumulation: float
    local_day_nc_rain_accumulation: float
    precipitation_analysis_type: PrecipitationAnalysisType

    def __post_init__(self):
        # Transform the raw observation data into the correct instances
        self.precipitation_type = PrecipitationType(self.precipitation_type)
        self.precipitation_analysis_type = PrecipitationAnalysisType(
            self.precipitation_analysis_type
        )


@dataclass
class obs_air(base_obs):
    """Dataclass for the air observation type."""

    epoch: int
    station_pressure: float
    air_temperature: float
    relative_humidity: int
    lightning_strike_count: int
    lightning_strike_average_distance: float
    battery: float
    report_interval: int


class ObservationFactory:
    """Factory class for creating observation instances from lists."""

    @staticmethod
    def create_observation(
        obs_type: ObservationType, obs_data: List[List[Any]]
    ) -> List[Union[obs_sky, obs_st, obs_air]]:
        """Create observation instances from a list of lists."""

        # if type(obs_data[0]) != list:
        #     print("OBS Data is already correct - aborting")
        #     return obs_data

        obs_class_map = {
            ObservationType.OBS_SKY: obs_sky,
            ObservationType.OBS_ST: obs_st,
            ObservationType.OBS_AIR: obs_air,
        }
        obs_class = obs_class_map.get(obs_type)
        if not obs_class:
            raise ValueError(f"Unknown observation type: {obs_type}")
        return [obs_class.from_list(obs_item) for obs_item in obs_data]


@dataclass
class WebsocketObservation:
    """Dataclass for the websocket observation type."""

    type: ObservationType
    device_id: int
    obs: List[Union[obs_sky, obs_st, obs_air]]

    def __post_init__(self):
        # Transform the raw observation data into the correct instances
        self.type = ObservationType(self.type)

        # TODO: Figure out why sometimes this gets called twice and why we need the logic
        # if not isinstance(self.obs[0], (obs_sky, obs_st, obs_air)):
        self.obs = ObservationFactory.create_observation(self.type, self.obs)

    #
    # @classmethod
    # def from_json(cls, json_data: dict[str, Any]) -> "WebsocketObservation":
    #     """Create a WebsocketObservation instance from a JSON dictionary."""
    #     obs_type = ObservationType(json_data["type"])
    #     obs_data: list[obs_sky | obs_air | obs_st] = json_data["obs"]
    #     observation_instances = ObservationFactory.create_observation(
    #         obs_type, obs_data
    #     )
    #     return cls(
    #         type=obs_type, device_id=json_data["device_id"], obs=observation_instances
    #     )
    #
    # @classmethod
    # def from_dict(cls, data: dict[str, Any]) -> "WebsocketObservation":
    #     """Create a WebsocketObservation instance from a dictionary."""
    #     obs_type = ObservationType(data["type"])
    #     obs_data: list[obs_sky | obs_air | obs_st] = data["obs"]
    #     observation_instances = ObservationFactory.create_observation(
    #         obs_type, obs_data
    #     )
    #     return cls(
    #         type=obs_type, device_id=data["device_id"], obs=observation_instances
    #     )

    @property
    def first(self) -> obs_sky | obs_air | obs_st:
        """Return the first observation instance."""
        return self.obs[0]

    @property
    def epoch(self) -> int:
        return self.first.epoch

    @property
    def wind_lull(self) -> float:
        return self.first.wind_lull

    @property
    def wind_avg(self) -> float:
        return self.first.wind_avg

    @property
    def wind_gust(self) -> float:
        return self.first.wind_gust

    @property
    def wind_direction(self) -> int:
        return self.first.wind_direction

    @property
    def wind_sample_interval(self) -> int:
        return self.first.wind_sample_interval

    @property
    def pressure(self) -> float:
        return self.first.pressure

    @property
    def air_temperature(self) -> float:
        return self.first.air_temperature

    @property
    def relative_humidity(self) -> int:
        return self.first.relative_humidity

    @property
    def illuminance(self) -> int:
        return self.first.illuminance

    @property
    def uv(self) -> float:
        return self.first.uv

    @property
    def solar_radiation(self) -> float:
        return self.first.solar_radiation

    @property
    def rain_accumulation(self) -> float:
        return self.first.rain_accumulation

    @property
    def precipitation_type(self) -> PrecipitationType:
        return self.first.precipitation_type

    @property
    def average_strike_distance(self) -> int:
        return self.first.average_strike_distance

    @property
    def strike_count(self) -> int:
        return self.first.strike_count

    @property
    def battery(self) -> float:
        return self.first.battery

    @property
    def report_interval(self) -> int:
        return self.first.report_interval

    @property
    def local_day_rain_accumulation(self) -> float:
        return self.first.local_day_rain_accumulation

    @property
    def nc_rain_accumulation(self) -> float:
        return self.first.nc_rain_accumulation

    @property
    def local_day_nc_rain_accumulation(self) -> float:
        return self.first.local_day_nc_rain_accumulation

    @property
    def precipitation_analysis_type(self) -> PrecipitationAnalysisType:
        return self.first.precipitation_analysis_type


# def construct_obs_st(sky: obs_sky, air: obs_air) -> obs_st:
#     return obs_st(
#         epoch=sky.epoch,  # Assuming the epochs are the same
#         wind_lull=sky.wind_lull,
#         wind_avg=sky.wind_avg,
#         wind_gust=sky.wind_gust,
#         wind_direction=sky.wind_direction,
#         wind_sample_interval=sky.wind_sample_interval,
#         pressure=air.station_pressure,
#         air_temperature=air.air_temperature,
#         relative_humidity=air.relative_humidity,
#         illuminance=sky.illuminance,
#         uv=sky.uv,
#         solar_radiation=sky.solar_radiation,
#         rain_accumulation=sky.rain_accumulation,
#         precipitation_type=sky.precipitation_type,
#         average_strike_distance=air.lightning_strike_average_distance,
#         strike_count=air.lightning_strike_count,
#         battery=sky.battery,  # Assuming the battery levels are the same
#         report_interval=sky.report_interval,
#         local_day_rain_accumulation=sky.local_day_rain_accumulation,
#         nc_rain_accumulation=sky.nc_rain,  # Assuming nc_rain is the same as nc_rain_accumulation
#         local_day_nc_rain_accumulation=sky.local_day_nc_rain_accumulation,
#         precipitation_analysis_type=sky.precipitation_analysis_type
#     )
