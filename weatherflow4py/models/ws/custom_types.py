"""Custom websocket types."""
from enum import Enum


class ObservationType(Enum):
    """Enumeration of the different observation types."""

    OBS_SKY = "obs_sky"
    OBS_ST = "obs_st"
    OBS_AIR = "obs_air"


class PrecipitationType(Enum):
    """(0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))"""

    NONE = 0
    RAIN = 1
    HAIL = 2
    RAIN_AND_HAIL = 3


class PrecipitationAnalysisType(Enum):
    """0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user display off"""

    NONE = 0
    RAIN_CHECK_WITH_USER_DISPLAY_ON = 1
    RAIN_CHECK_WITH_USER_DISPLAY_OFF = 2
