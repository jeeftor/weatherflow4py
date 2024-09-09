from dataclasses import dataclass

from dataclasses_json import dataclass_json
from weatherflow4py.const import BASE_LOGGER


@dataclass_json
@dataclass
class Status:
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
