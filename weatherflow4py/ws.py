import time
from collections.abc import Callable

import asyncio
import websockets
import json

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    WebsocketRequest,
    ListenStopMessage,
    RapidWindListenStopMessage,
)
from weatherflow4py.models.ws.websocket_response import (
    WebsocketResponseBuilder,
    ObservationTempestWS,
    RapidWindWS,
)

from .const import LOGGER


class WeatherFlowWebsocketAPI:
    def __init__(self, device_id: str, access_token: str):
        self.device_id = device_id
        self.uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
        self.websocket = None
        self.messages = {}
        self.is_listening = False
        self.listen_task = None  # To keep track of the listening task
        self.callbacks = {}

        LOGGER.debug("WebsocketAPI initialized with URI: " + self.uri)

    def _register_callback(
        self, message_type: EventType, callback: Callable[[str], None]
    ):
        """Register a callback for a specific message type"""
        self.callbacks[message_type.value] = callback

    def register_invalid_data_callback(self, callback: Callable[[str], None]):
        """
        Register a callback for the 'invalid' event.

        The callback should be a function that takes a single argument of type str.

        Example:
            def invalid_callback(data: str):
                print("Received invalid data:", data)

            api = WebsocketAPI(device_id, access_token)
            api.register_invalid(invalid_callback)

        Args:
            callback (Callable[[str], None]): The callback function to register.
        """
        self.callbacks[EventType.INVALID.value] = callback

    def register_wind_callback(self, callback: Callable[[RapidWindWS], None]):
        """
        Register a callback for the 'rapid_wind' event.

        The callback should be a function that takes a single argument of type RapidWindWS.

        Example:
            def wind_callback(data: RapidWindWS):
                print("Received wind data:", data)

            api = WebsocketAPI(device_id, access_token)
            api.register_wind_callback(wind_callback)

        Args:
            callback (Callable[[RapidWindWS], None]): The callback function to register.
        """
        self.callbacks[EventType.RAPID_WIND.value] = callback

    def register_precipitation_callback(self, callback: Callable[[str], None]):
        """
        Register a callback for the 'rain' event.

        The callback should be a function that takes a single argument of type str.

        Example:
            def rain_callback(data: str):
                print("Received rain data:", data)

            api = WebsocketAPI(device_id, access_token)
            api.register_precipitation_callback(rain_callback)

        Args:
            callback (Callable[[str], None]): The callback function to register.
        """
        self.callbacks[EventType.RAIN.value] = callback

    def register_lightning_callback(self, callback: Callable[[str], None]):
        """
        Register a callback for the 'lightning_strike' event.

        The callback should be a function that takes a single argument of type str.

        Example:
            def lightning_callback(data: str):
                print("Received lightning data:", data)

            api = WebsocketAPI(device_id, access_token)
            api.register_lightning_callback(lightning_callback)

        Args:
            callback (Callable[[str], None]): The callback function to register.
        """
        self.callbacks[EventType.LIGHTNING_STRIKE.value] = callback

    def register_observation_callback(
        self, callback: Callable[[ObservationTempestWS], None]
    ):
        """
        Register a callback for the 'obs_st' event.

        The callback should be a function that takes a single argument of type ObservationTempestWS.

        Example:
            def observation_callback(data: ObservationTempestWS):
                print("Received observation data:", data)

            api = WebsocketAPI(device_id, access_token)
            api.register_observation_callback(observation_callback)

        Args:
            callback (Callable[[ObservationTempestWS], None]): The callback function to register.
        """
        self.callbacks[EventType.OBSERVATION.value] = callback

    @property
    def last_observation(self) -> ObservationTempestWS | None:
        """Last observation"""
        return self.messages.get("obs_st")

    def last_wind(self) -> RapidWindWS | None:
        return self.messages.get("rapid_wind")

    def last_observation_time(self) -> float | None:
        """Seconds since last observation"""
        current_epoch = time.time()
        if obs := self.last_observation:
            last_observation_epoch = obs.epoch
            time_difference = current_epoch - last_observation_epoch
            return time_difference
        return None

    async def send_message(self, message_type: WebsocketRequest):
        message = message_type.json
        LOGGER.debug(f"Sending message: {message}")
        await self._send(message)

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        # Run the listen method in the background and name the task for easier debugging
        self.listen_task = asyncio.create_task(
            self.listen(), name="WebSocketListenTask"
        )

    async def listen(self):
        self.is_listening = True
        try:
            async for message in self.websocket:
                LOGGER.debug(f"Received message: {message}")
                data = json.loads(message)
                try:
                    response = WebsocketResponseBuilder.build_response(data)
                    self.messages[data["type"]] = response

                    if data["type"] in self.callbacks:
                        if asyncio.iscoroutinefunction(self.callbacks[data["type"]]):
                            LOGGER.debug(
                                f"Calling ASYNC callback for message type: {data['type']}"
                            )
                            # If it is, use 'await' to call it
                            await self.callbacks[data["type"]](response)
                        else:
                            LOGGER.debug(
                                f"Calling SYNC callback for message type: {data['type']}"
                            )
                            # If it's not, call it normally
                            self.callbacks[data["type"]](response)
                    else:
                        LOGGER.debug(f"NO CALLBACK for message type: {data['type']}")
                except ValueError:
                    if EventType.INVALID.value in self.callbacks:
                        if asyncio.iscoroutinefunction(
                            self.callbacks[EventType.INVALID.value]
                        ):
                            # If it is, use 'await' to call it
                            await self.callbacks[EventType.INVALID.value](data)
                        else:
                            # If it's not, call it normally
                            self.callbacks[EventType.INVALID.value](data)
                    else:
                        print(f"INVALID:\n {message}")

                    continue

        finally:
            self.is_listening = False

    async def _send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def is_connected(self):
        # Check if the websocket connection is open
        return self.websocket and not self.websocket.closed

    async def close(self):
        await self.send_message(ListenStopMessage(device_id=self.device_id))
        await self.send_message(RapidWindListenStopMessage(device_id=self.device_id))

        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.listen_task:
            self.listen_task.cancel()  # Cancel the listening task
            try:
                await self.listen_task  # Await the task to handle cancellation
            except asyncio.CancelledError:
                pass  # Task cancellation is expected
