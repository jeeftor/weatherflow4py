from enum import Enum


class EventType(Enum):
    ACKNOWLEDGEMENT = "ack"
    RAPID_WIND = "rapid_wind"
    OBSERVATION = "obs_st"
    LIGHTNING_STRIKE = "evt_strike"
    RAIN = "evt_precip"
    DEVICE_STATUS = "device_status"
    INVALID = "unknown"


class MessageType(Enum):
    LISTEN_START = "listen_start"
    LISTEN_STOP = "listen_stop"
    RAPID_WIND_START = "listen_rapid_start"
    RAPID_WIND_STOP = "listen_rapid_stop"


class LightingStrikeType:
    ALL = "all"
    CLOUD_TO_GROUND = "cg"
    CLOUD_TO_CLOUD = "ic"
