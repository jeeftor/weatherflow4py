import time
from collections.abc import Callable

import asyncio
from ssl import SSLContext

import websockets
import websockets.asyncio.client
from websockets.connection import State as WebSocketState
from websockets.exceptions import WebSocketException
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
    AcknowledgementWS,
)

from .const import WS_LOGGER


class WeatherFlowWebsocketAPI:
    """Websocket API For Weatherflow Devices."""

    _shared_websocket = None  # Class variable for the WebSocket connection
    _lock = asyncio.Lock()  # Async lock for websocket initialization

    _LISTEN_START_TYPES = {
        "listen_start",
        "listen_rapid_start",
        "geo_strike_listen_start",
    }
    _STOP_MESSAGE_TYPES = {
        "listen_start": ListenStopMessage,
        "listen_rapid_start": RapidWindListenStopMessage,
    }
    _STOP_TO_START_TYPES = {
        "listen_stop": "listen_start",
        "listen_rapid_stop": "listen_rapid_start",
    }
    _RECONNECT_MIN_DELAY = 1.0
    _RECONNECT_MAX_DELAY = 60.0

    def __init__(self, access_token: str, device_ids=None):
        if device_ids is None:
            device_ids = []
        self.device_ids = device_ids
        self.uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
        self.websocket: websockets.asyncio.client.ClientConnection | None = None
        self.messages = {}
        self.is_listening = False
        self.listen_task = None  # To keep track of the listening task
        self.callbacks = {}
        self._closing = False
        self._ssl_context: SSLContext | None = None
        self._subscriptions: dict[tuple[str, str], WebsocketRequest] = {}

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

    def _update_subscriptions(self, message: WebsocketRequest) -> None:
        """Track listen subscriptions so they can be restored on reconnect."""
        device_id = getattr(message, "device_id", message.id)
        if message.type in self._LISTEN_START_TYPES:
            self._subscriptions[(message.type, device_id)] = message
        elif start_type := self._STOP_TO_START_TYPES.get(message.type):
            self._subscriptions.pop((start_type, device_id), None)

    async def send_message(self, message_type: WebsocketRequest):
        message = message_type.json
        WS_LOGGER.debug(f"Sending message: {message}")
        await self._send(message)
        self._update_subscriptions(message_type)

    async def send_message_and_wait(
        self, message_type: WebsocketRequest, timeout: float = 5.0
    ) -> AcknowledgementWS | None:
        message = message_type.json
        WS_LOGGER.debug(f"Sending message and waiting for ACK: {message}")

        # Create a future to store the ACK response
        ack_future = asyncio.Future()

        # Register a temporary callback for ACK messages
        def ack_callback(ack: AcknowledgementWS):
            if not ack_future.done():
                ack_future.set_result(ack)

        # Store the original ACK callback if it exists
        original_ack_callback = self.callbacks.get(EventType.ACKNOWLEDGEMENT.value)

        # Set our temporary callback
        self.callbacks[EventType.ACKNOWLEDGEMENT.value] = ack_callback

        try:
            # Send the message
            await self._send(message)
            self._update_subscriptions(message_type)

            # Wait for the ACK with a timeout
            return await asyncio.wait_for(ack_future, timeout=timeout)

        except TimeoutError:
            WS_LOGGER.warning(f"Timeout waiting for ACK after sending: {message}")
            return None
        except (WebSocketException, OSError) as err:
            WS_LOGGER.warning(f"Failed to send message {message}: {err}")
            return None

        finally:
            # Restore the original callback or remove our temporary one
            if original_ack_callback:
                self.callbacks[EventType.ACKNOWLEDGEMENT.value] = original_ack_callback
            else:
                self.callbacks.pop(EventType.ACKNOWLEDGEMENT.value, None)

    async def _open_websocket(self) -> None:
        """Open the shared websocket if it is missing or no longer open."""
        async with WeatherFlowWebsocketAPI._lock:
            shared = WeatherFlowWebsocketAPI._shared_websocket
            if shared is None or shared.state is not WebSocketState.OPEN:
                kwargs = {"ssl": self._ssl_context} if self._ssl_context else {}
                shared = await websockets.connect(self.uri, **kwargs)
                WeatherFlowWebsocketAPI._shared_websocket = shared
                WS_LOGGER.debug(f"WebSocket connected at memory address: {id(shared)}")

            self.websocket = shared

    async def connect(self, ssl_context: SSLContext | None = None):
        """Establishes a WebSocket connection and starts a background listening task.

        :param ssl_context: Optional SSL context for secure connections
        """
        self._ssl_context = ssl_context
        self._closing = False
        await self._open_websocket()

        # Run the listen method in the background and name the task for easier debugging
        self.listen_task = asyncio.create_task(
            self.listen(), name="WebSocketListenTask"
        )

    async def _reconnect(self) -> bool:
        """Reopen the websocket and restore subscriptions.

        Returns True once reconnected, or False when close() was requested.
        """
        delay = self._RECONNECT_MIN_DELAY
        while not self._closing:
            try:
                await self._open_websocket()
                for subscription in list(self._subscriptions.values()):
                    await self.send_message(subscription)
            except asyncio.CancelledError:
                raise
            except (WebSocketException, OSError, TimeoutError) as err:
                WS_LOGGER.warning(
                    f"Websocket reconnect failed ({err}); retrying in {delay:.0f} s"
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._RECONNECT_MAX_DELAY)
            else:
                WS_LOGGER.info("WeatherFlow websocket reconnected")
                return True
        return False

    async def listen(self):
        """Dispatch websocket messages, reconnecting if the connection drops."""
        self.is_listening = True
        assert self.websocket is not None
        try:
            while True:
                try:
                    async for message in self.websocket:
                        try:
                            await self._handle_message(message)
                        except Exception:
                            WS_LOGGER.exception(
                                f"Failed to handle websocket message: {message}"
                            )
                except asyncio.CancelledError:
                    raise
                except Exception as err:
                    WS_LOGGER.warning(f"Websocket connection lost: {err}")
                finally:
                    self.is_listening = False

                if self._closing or not await self._reconnect():
                    break
                self.is_listening = True
        finally:
            self.is_listening = False

    async def _handle_message(self, message: str) -> None:
        """Parse a raw websocket message and dispatch it to callbacks."""
        WS_LOGGER.debug(f"Received message: {message}")
        data = json.loads(message)
        try:
            response = WebsocketResponseBuilder.build_response(data)
            if response is None:
                WS_LOGGER.info(f"Received invalid WS Status Message {data}")
            self.messages[data["type"]] = response

            if data["type"] in self.callbacks:
                if asyncio.iscoroutinefunction(self.callbacks[data["type"]]):
                    WS_LOGGER.debug(
                        f"Calling ASYNC callback for message type: {data['type']}"
                    )
                    # If it is, use 'await' to call it
                    await self.callbacks[data["type"]](response)
                else:
                    WS_LOGGER.debug(
                        f"Calling SYNC callback for message type: {data['type']}"
                    )
                    # If it's not, call it normally
                    self.callbacks[data["type"]](response)
            else:
                WS_LOGGER.debug(f"NO CALLBACK for message type: {data['type']}")
        except ValueError:
            if EventType.INVALID.value in self.callbacks:
                if asyncio.iscoroutinefunction(self.callbacks[EventType.INVALID.value]):
                    # If it is, use 'await' to call it
                    await self.callbacks[EventType.INVALID.value](data)
                else:
                    # If it's not, call it normally
                    self.callbacks[EventType.INVALID.value](data)
            else:
                WS_LOGGER.warning(f"Unrecognized WS Message: {message}")

    async def _send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def is_connected(self):
        # Check if the websocket connection is open
        return (
            self.websocket is not None and self.websocket.state is WebSocketState.OPEN
        )

    async def stop_all_listeners(self):
        """
        Stop listening for all devices - waits for acknowledgement
        """
        subscriptions = [
            (msg_type, device_id)
            for msg_type, device_id in self._subscriptions
            if msg_type in self._STOP_MESSAGE_TYPES
        ]
        self._subscriptions.clear()

        if not self.is_connected():
            return

        covered_ids = set()
        for msg_type, device_id in subscriptions:
            covered_ids.add(str(device_id))
            await self.send_message_and_wait(
                self._STOP_MESSAGE_TYPES[msg_type](device_id=device_id)
            )

        for device_id in self.device_ids:
            if str(device_id) in covered_ids:
                continue
            await self.send_message_and_wait(ListenStopMessage(device_id=device_id))
            await self.send_message_and_wait(
                RapidWindListenStopMessage(device_id=device_id)
            )

        WS_LOGGER.debug("Stopped listening for all devices 🙉️")

    async def close(self, timeout: float = 5.0) -> None:
        """
        Close the WebSocket connection and clean up resources.

        Args:
            timeout (float): Maximum time to wait for tasks to complete (default: 5.0 seconds)
        """
        self._closing = True
        await self.stop_all_listeners()

        # Cancel the listen task
        if self.listen_task and not self.listen_task.done():
            self.listen_task.cancel()
            try:
                await asyncio.wait_for(self.listen_task, timeout=timeout)
            except TimeoutError:
                WS_LOGGER.warning("Listen task cancellation timed out")
            except asyncio.CancelledError:
                WS_LOGGER.debug("Listen task was cancelled")
            except Exception as e:
                WS_LOGGER.error(f"Exception during listen task cancellation: {e}")

        # Close the WebSocket connection
        websocket = self.websocket
        if websocket is not None:
            WS_LOGGER.debug(
                f"Attempting to close WebSocket at memory address: {id(websocket)}"
            )
            try:
                await asyncio.wait_for(websocket.close(), timeout=timeout)
            except TimeoutError:
                WS_LOGGER.warning("WebSocket close operation timed out")
            except (WebSocketException, OSError) as e:
                WS_LOGGER.debug(f"WebSocket close failed: {e}")
            except Exception as e:
                WS_LOGGER.error(f"Exception during WebSocket close operation: {e}")
            finally:
                if WeatherFlowWebsocketAPI._shared_websocket is websocket:
                    WeatherFlowWebsocketAPI._shared_websocket = None
                self.websocket = None

        self.is_listening = False
        WS_LOGGER.debug("WebSocket connection closed and resources cleaned up")
