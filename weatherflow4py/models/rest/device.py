from dataclasses import dataclass
from typing import List, Optional, Union

from dataclasses_json import dataclass_json

from weatherflow4py.models.rest.status import Status
from weatherflow4py.models.ws.custom_types import (
    PrecipitationAnalysisType,
    ObservationType,
)
from weatherflow4py.models.ws.obs import (
    obs_st,
    WebsocketObservation,
    obs_sky,
    obs_air,
    ObservationFactory,
)


@dataclass_json
@dataclass
class Summary:
    strike_count_1h: int
    strike_count_3h: int
    precip_total_1h: float
    precip_accum_local_yesterday: float
    precip_analysis_type_yesterday: PrecipitationAnalysisType
    feels_like: float
    heat_index: float
    wind_chill: float
    pressure_trend: Optional[str] = None
    precip_accum_local_yesterday_final: Optional[float] = None
    strike_last_dist: Optional[int] = None
    strike_last_epoch: Optional[int] = None


@dataclass_json
@dataclass
class DeviceObservationREST:
    """Higher level class used by REST"""

    status: Status
    device_id: int
    type: ObservationType
    source: str
    summary: Summary
    obs: List[Union[obs_sky, obs_st, obs_air]]  # Add this line

    #
    def __post_init__(self):
        # Transform the raw observation data into the correct instances
        self.obs = ObservationFactory.create_observation(self.type, self.obs)


@dataclass_json
@dataclass
class DeviceObservationTempestREST(DeviceObservationREST, WebsocketObservation):
    """Wrap it up."""
