import time
from collections.abc import Callable

import asyncio
from ssl import SSLContext

import websockets
import websockets.asyncio.client
from websockets.connection import State as WebSocketState
from websockets.exceptions import ConnectionClosed
import json

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    GeoStrikeListenStartMessage,
    ListenStartMessage,
    ListenStopMessage,
    RapidWindListenStartMessage,
    RapidWindListenStopMessage,
    WebsocketRequest,
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
        self._active_subscriptions: list[WebsocketRequest] = []
        self._shutting_down = False
        self._ssl_context: SSLContext | None = None

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

    def _track_subscription(self, message_type: WebsocketRequest) -> None:
        """Track listen_start/stop messages so they can be replayed after reconnect."""
        if isinstance(
            message_type,
            (
                ListenStartMessage,
                RapidWindListenStartMessage,
                GeoStrikeListenStartMessage,
            ),
        ):
            self._active_subscriptions.append(message_type)
        elif isinstance(message_type, ListenStopMessage):
            self._active_subscriptions = [
                m
                for m in self._active_subscriptions
                if not (
                    isinstance(m, ListenStartMessage)
                    and m.device_id == message_type.device_id
                )
            ]
        elif isinstance(message_type, RapidWindListenStopMessage):
            self._active_subscriptions = [
                m
                for m in self._active_subscriptions
                if not (
                    isinstance(m, RapidWindListenStartMessage)
                    and m.device_id == message_type.device_id
                )
            ]

    async def send_message(self, message_type: WebsocketRequest):
        message = message_type.json
        WS_LOGGER.debug(f"Sending message: {message}")
        await self._send(message)
        self._track_subscription(message_type)

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
            self._track_subscription(message_type)

            # Wait for the ACK with a timeout
            return await asyncio.wait_for(ack_future, timeout=timeout)

        except TimeoutError:
            WS_LOGGER.warning(f"Timeout waiting for ACK after sending: {message}")
            return None

        finally:
            # Restore the original callback or remove our temporary one
            if original_ack_callback:
                self.callbacks[EventType.ACKNOWLEDGEMENT.value] = original_ack_callback
            else:
                self.callbacks.pop(EventType.ACKNOWLEDGEMENT.value, None)

    async def connect(self, ssl_context: SSLContext | None = None):
        """Establishes a WebSocket connection and starts a background listening task.

        The listening task includes a supervisor that automatically reconnects
        with exponential backoff when the server closes the connection (e.g.
        idle timeout, keepalive ping timeout), replaying all active
        subscriptions after each successful reconnect.

        :param ssl_context: Optional SSL context for secure connections
        """
        self._ssl_context = ssl_context
        self._shutting_down = False
        await self._open_connection(ssl_context)

        # Run the supervisor in the background; it calls listen() and
        # reconnects on unexpected disconnect.
        self.listen_task = asyncio.create_task(
            self._listen_supervisor(), name="WebSocketListenSupervisor"
        )

    async def _open_connection(self, ssl_context: SSLContext | None = None) -> None:
        """Open the shared websocket connection if not already open.

        Does not start a listen task — the supervisor handles that.
        """
        async with WeatherFlowWebsocketAPI._lock:
            if WeatherFlowWebsocketAPI._shared_websocket is None:
                if ssl_context is None:
                    WeatherFlowWebsocketAPI._shared_websocket = (
                        await websockets.connect(self.uri)
                    )
                else:
                    WeatherFlowWebsocketAPI._shared_websocket = (
                        await websockets.connect(self.uri, ssl=ssl_context)
                    )

                WS_LOGGER.debug(
                    f"WebSocket connected at memory address: {id(WeatherFlowWebsocketAPI._shared_websocket)}"
                )

            self.websocket = WeatherFlowWebsocketAPI._shared_websocket

    async def _listen_supervisor(self) -> None:
        """Run listen() in a loop, reconnecting on unexpected disconnect."""
        while not self._shutting_down:
            # Yield to the event loop each iteration so close() can run even
            # when listen() returns instantly (e.g. already-closed socket).
            await asyncio.sleep(0)
            try:
                await self.listen()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                WS_LOGGER.warning(f"Listen loop exited with error: {e!r}")

            if self._shutting_down:
                break

            WS_LOGGER.info("WebSocket disconnected, attempting reconnect...")
            if not await self._reconnect():
                WS_LOGGER.error("Reconnect failed, supervisor exiting")
                break

    async def _reconnect(
        self,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
    ) -> bool:
        """Reconnect with exponential backoff and replay subscriptions.

        Retries indefinitely until the connection succeeds or ``_shutting_down``
        is set. Returns ``True`` on success, ``False`` if interrupted by shutdown.
        """
        backoff = initial_backoff
        attempt = 0
        while not self._shutting_down:
            attempt += 1
            try:
                # Clear the dead shared websocket so _open_connection opens a
                # fresh one. Only clear it if it's the same object we're
                # holding — another instance may have already reconnected.
                async with WeatherFlowWebsocketAPI._lock:
                    if (
                        WeatherFlowWebsocketAPI._shared_websocket is not None
                        and WeatherFlowWebsocketAPI._shared_websocket is self.websocket
                    ):
                        WeatherFlowWebsocketAPI._shared_websocket = None
                    self.websocket = None

                await self._open_connection(self._ssl_context)
                await self._replay_subscriptions()
                WS_LOGGER.info(f"WebSocket reconnected on attempt {attempt}")
                return True
            except asyncio.CancelledError:
                raise
            except Exception as e:
                WS_LOGGER.warning(f"Reconnect attempt {attempt} failed: {e!r}")
                if self._shutting_down:
                    return False
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
        return False

    async def _replay_subscriptions(self) -> None:
        """Resend all active listen_start subscriptions after reconnecting.

        Uses ``_send`` directly rather than ``send_message`` to avoid
        double-tracking subscriptions that are already in the list.
        """
        for message in list(self._active_subscriptions):
            try:
                await self._send(message.json)
            except Exception as e:
                WS_LOGGER.warning(
                    f"Failed to replay subscription {message.to_dict()}: {e!r}"
                )

    async def listen(self):
        self.is_listening = True
        assert self.websocket is not None
        try:
            async for message in self.websocket:
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
                        if asyncio.iscoroutinefunction(
                            self.callbacks[EventType.INVALID.value]
                        ):
                            # If it is, use 'await' to call it
                            await self.callbacks[EventType.INVALID.value](data)
                        else:
                            # If it's not, call it normally
                            self.callbacks[EventType.INVALID.value](data)
                    else:
                        WS_LOGGER.warning(f"Unrecognized WS Message: {message}")

                    continue

        finally:
            self.is_listening = False

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
        if not self.is_connected():
            WS_LOGGER.debug("Skipping stop_all_listeners - websocket not connected")
            return

        stop_coros = []
        for device_id in self.device_ids:
            stop_coros.extend(
                [
                    self.send_message_and_wait(ListenStopMessage(device_id=device_id)),
                    self.send_message_and_wait(
                        RapidWindListenStopMessage(device_id=device_id)
                    ),
                ]
            )

        # gather with return_exceptions so a single failure (e.g. the server
        # already closed the socket) doesn't leave the remaining coroutines
        # unawaited, which previously produced
        # "RuntimeWarning: coroutine 'send_message_and_wait' was never awaited".
        results = await asyncio.gather(*stop_coros, return_exceptions=True)
        for result in results:
            if isinstance(result, ConnectionClosed):
                WS_LOGGER.debug(f"stop_all_listeners send failed: {result!r}")
            elif isinstance(result, BaseException):
                WS_LOGGER.warning(f"Unexpected error stopping listener: {result!r}")

        WS_LOGGER.debug("Stopped listening for all devices 🙉️")

    async def close(self, timeout: float = 5.0) -> None:
        """
        Close the WebSocket connection and clean up resources.

        Args:
            timeout (float): Maximum time to wait for tasks to complete (default: 5.0 seconds)
        """
        # Signal the supervisor to stop reconnecting before we tear anything down.
        self._shutting_down = True

        # Capture the connection before nulling anything so we can clear the
        # class-level reference even on the early-return path.
        websocket = self.websocket

        if not self.is_connected():
            # The socket is already gone (e.g. server idle timeout). Clear the
            # class-level reference so a subsequent connect() opens a fresh
            # socket instead of reusing this dead one.
            if (
                websocket is not None
                and WeatherFlowWebsocketAPI._shared_websocket is websocket
            ):
                WeatherFlowWebsocketAPI._shared_websocket = None
            self.websocket = None
            self.is_listening = False
            self._active_subscriptions.clear()
            return

        await self.stop_all_listeners()

        # Cancel the listen task (supervisor)
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
        if self.websocket:
            WS_LOGGER.debug(
                f"Attempting to close WebSocket at memory address: {id(self.websocket)}"
            )
            try:
                await asyncio.wait_for(self.websocket.close(), timeout=timeout)
            except TimeoutError:
                WS_LOGGER.warning("WebSocket close operation timed out")
            except Exception as e:
                WS_LOGGER.error(f"Exception during WebSocket close operation: {e}")
            finally:
                if self.websocket.state is WebSocketState.CLOSED:
                    WS_LOGGER.debug("WebSocket connection successfully closed")
                else:
                    WS_LOGGER.warning("WebSocket connection not closed")
                self.websocket = None

        # Clear the class-level reference so a subsequent connect() opens a new
        # socket rather than reusing the (now closed) shared one.
        if (
            websocket is not None
            and WeatherFlowWebsocketAPI._shared_websocket is websocket
        ):
            WeatherFlowWebsocketAPI._shared_websocket = None

        self._active_subscriptions.clear()
        self.is_listening = False
        WS_LOGGER.debug("WebSocket connection closed and resources cleaned up")
