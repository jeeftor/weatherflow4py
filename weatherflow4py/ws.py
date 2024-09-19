import time
from collections.abc import Callable

import asyncio
from ssl import SSLContext
from typing import Optional

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

from .const import WS_LOGGER


class WeatherFlowWebsocketAPI:
    """Websocket API For Weatherflow Devices."""

    def __init__(self, access_token: str, device_ids=None):
        if device_ids is None:
            device_ids = []
        self.device_ids = device_ids
        self.uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
        self.websocket = None
        self.messages = {}
        self.is_listening = False
        self.listen_task = None  # To keep track of the listening task
        self.callbacks = {}

        # Closing support events
        self._closing = asyncio.Event()
        self._closed = asyncio.Event()

        WS_LOGGER.debug("WebsocketAPI initialized with URI: " + self.uri)

    def register_callback(
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

            api = WebsocketAPI(access_token, device_id )
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

            api = WebsocketAPI(access_token, [device_id1, device_id2])
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

            api = WebsocketAPI(access_token, [device_id1, device_id2])
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

            api = WebsocketAPI(access_token)
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
        WS_LOGGER.debug(f"Sending message: {message}")
        await self._send(message)


    async def connect(self, ssl_context: Optional[SSLContext] = None):
        """Establishes a WebSocket connection and starts a background listening task.

           :param ssl_context: Optional SSL context for secure connections
        """
        if ssl_context is None:
            self.websocket = await websockets.connect(self.uri)
        else:
            self.websocket = await websockets.connect(self.uri, ssl=ssl_context)

        # Run the listen method in the background and name the task for easier debugging
        self.listen_task = asyncio.create_task(
            self.listen(), name="WebSocketListenTask"
        )

    async def listen(self):
        self.is_listening = True
        try:
            while not self._closing.is_set():
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    WS_LOGGER.debug(f"Received message: {message}")
                    await self.process_message(message)
                except asyncio.TimeoutError:
                    continue  # Allow checking the closing flag
                except websockets.ConnectionClosed:
                    if not self._closing.is_set():
                        WS_LOGGER.error("WebSocket connection closed unexpectedly")
                    break
                except json.JSONDecodeError as e:
                    WS_LOGGER.error(f"JSON decode error: {e}")
                    continue
                except Exception as e:
                    if not self._closing.is_set():
                        WS_LOGGER.error(f"Error in WebSocket listener: {e}")
                    break
        finally:
            self.is_listening = False
            self._closed.set()
            WS_LOGGER.debug("WebSocket listener stopped")

    async def process_message(self, message: str):
        try:
            data = json.loads(message)
            response = WebsocketResponseBuilder.build_response(data)
            self.messages[data["type"]] = response

            if data["type"] in self.callbacks:
                callback = self.callbacks[data["type"]]
                if asyncio.iscoroutinefunction(callback):
                    WS_LOGGER.debug(f"Calling ASYNC callback for message type: {data['type']}")
                    await callback(response)
                else:
                    WS_LOGGER.debug(f"Calling SYNC callback for message type: {data['type']}")
                    callback(response)
            else:
                WS_LOGGER.debug(f"NO CALLBACK for message type: {data['type']}")
        except ValueError:
            if EventType.INVALID.value in self.callbacks:
                invalid_callback = self.callbacks[EventType.INVALID.value]
                if asyncio.iscoroutinefunction(invalid_callback):
                    await invalid_callback(data)
                else:
                    invalid_callback(data)
            else:
                WS_LOGGER.warning(f"Unrecognized WS Message: {message}")


    async def _send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def is_connected(self) -> bool:
        # Check if the websocket connection is open
        return self.websocket and not self.websocket.closed and not self._closing.is_set()

    async def close(self):
        """Close the WebSocket connection and stop the listening task."""
        WS_LOGGER.debug("Closing WebSocket connection")

        if self._closing.is_set():
            WS_LOGGER.debug("Close already in progress")
            await self._closed.wait()
            return

        self._closing.set()

        try:
            # Attempt to send stop messages first
            for device_id in self.device_ids:
                WS_LOGGER.debug(f"Unregistering Websocket Listener for device_id: {device_id}")
                try:
                    await asyncio.wait_for(
                        asyncio.gather(
                            self.send_message(ListenStopMessage(device_id=device_id)),
                            self.send_message(RapidWindListenStopMessage(device_id=device_id))
                        ),
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    WS_LOGGER.warning(f"Timeout sending stop messages for device_id: {device_id}")
                except Exception as e:
                    WS_LOGGER.error(f"Error sending stop messages for device_id {device_id}: {e}")

            # Close the WebSocket connection
            if self.websocket:
                try:
                    await self.websocket.close()
                except Exception as e:
                    WS_LOGGER.error(f"Error closing WebSocket: {e}")
                finally:
                    self.websocket = None

            # Wait for the listen task to complete
            if self.listen_task:
                try:
                    await asyncio.wait_for(self.listen_task, timeout=5.0)
                except asyncio.TimeoutError:
                    WS_LOGGER.warning("Timeout waiting for listen task to complete")
                except Exception as e:
                    WS_LOGGER.error(f"Error waiting for listen task to complete: {e}")
                finally:
                    self.listen_task = None

        finally:
            await self._closed.wait()
            WS_LOGGER.debug("WebSocket connection closed")
