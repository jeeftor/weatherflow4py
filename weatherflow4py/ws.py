import asyncio
import json
import logging
import time
from collections.abc import Callable, Awaitable
from ssl import SSLContext
from typing import Optional, Any, TypedDict, NotRequired

import websockets

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

WS_LOGGER = logging.getLogger(__name__)

class MessageDict(TypedDict):
    type: str
    data: NotRequired[Any]

class WeatherFlowWebsocketAPI:
    """Websocket API For Weatherflow Devices."""

    def __init__(self, access_token: str, device_ids: list[str] | None = None) -> None:
        self.device_ids: list[str] = device_ids or []
        self.uri: str = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
        self.websocket: websockets.WebSocketClientProtocol | None = None
        self.messages: dict[str, Any] = {}
        self.is_listening: bool = False
        self.listen_task: asyncio.Task[None] | None = None
        self.callbacks: dict[str, Callable[[Any], None] | Callable[[Any], Awaitable[None]]] = {}

        self._closing: asyncio.Event = asyncio.Event()
        self._closed: asyncio.Event = asyncio.Event()

        WS_LOGGER.debug("WebsocketAPI initialized with URI: %s", self.uri)

    def register_callback(
            self, message_type: EventType, callback: Callable[[Any], None] | Callable[[Any], Awaitable[None]]
    ) -> None:
        """Register a callback for a specific message type"""
        self.callbacks[message_type.value] = callback

    def register_invalid_data_callback(self, callback: Callable[[str], None] | Callable[[str], Awaitable[None]]) -> None:
        """Register a callback for the 'invalid' event."""
        self.callbacks[EventType.INVALID.value] = callback

    def register_wind_callback(self, callback: Callable[[RapidWindWS], None] | Callable[[RapidWindWS], Awaitable[None]]) -> None:
        """Register a callback for the 'rapid_wind' event."""
        self.callbacks[EventType.RAPID_WIND.value] = callback

    def register_precipitation_callback(self, callback: Callable[[str], None] | Callable[[str], Awaitable[None]]) -> None:
        """Register a callback for the 'rain' event."""
        self.callbacks[EventType.RAIN.value] = callback

    def register_lightning_callback(self, callback: Callable[[str], None] | Callable[[str], Awaitable[None]]) -> None:
        """Register a callback for the 'lightning_strike' event."""
        self.callbacks[EventType.LIGHTNING_STRIKE.value] = callback

    def register_observation_callback(
            self, callback: Callable[[ObservationTempestWS], None] | Callable[[ObservationTempestWS], Awaitable[None]]
    ) -> None:
        """Register a callback for the 'obs_st' event."""
        self.callbacks[EventType.OBSERVATION.value] = callback

    @property
    def last_observation(self) -> ObservationTempestWS | None:
        """Last observation"""
        return self.messages.get("obs_st")

    @property
    def last_wind(self) -> RapidWindWS | None:
        """Last wind observation"""
        return self.messages.get("rapid_wind")

    def last_observation_time(self) -> float | None:
        """Seconds since last observation"""
        if obs := self.last_observation:
            return time.time() - obs.epoch
        return None

    async def send_message(self, message_type: WebsocketRequest) -> None:
        message = message_type.json
        WS_LOGGER.debug("Sending message: %s", message)
        await self._send(message)

    async def connect(self, ssl_context: Optional[SSLContext] = None) -> None:
        """Establishes a WebSocket connection and starts a background listening task."""
        self.websocket = await websockets.connect(self.uri, ssl=ssl_context)
        self.listen_task = asyncio.create_task(self.listen(), name="WebSocketListenTask")

    async def listen(self) -> None:
        self.is_listening = True
        try:
            while not self._closing.is_set():
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    WS_LOGGER.debug("Received message: %s", message)
                    asyncio.create_task(self.process_message(message))
                except asyncio.TimeoutError:
                    continue
                except websockets.ConnectionClosed:
                    if not self._closing.is_set():
                        WS_LOGGER.error("WebSocket connection closed unexpectedly")
                    break
                except Exception as e:
                    if not self._closing.is_set():
                        WS_LOGGER.error("Error in WebSocket listener: %s", e)
                    break
        finally:
            self.is_listening = False
            self._closed.set()
            WS_LOGGER.debug("WebSocket listener stopped")

    async def process_message(self, message: str) -> None:
        try:
            data: MessageDict = json.loads(message)
            match data:
                case {"type": str(message_type), "data": dict() as message_data}:
                    response = await WebsocketResponseBuilder.build_response(message_data)
                    self.messages[message_type] = response

                    if callback := self.callbacks.get(message_type):
                        WS_LOGGER.debug("Calling callback for message type: %s", message_type)
                        await self._execute_callback(callback, response)
                    else:
                        WS_LOGGER.debug("No callback for message type: %s", message_type)
                case _:
                    raise ValueError("Unrecognized message format")
        except json.JSONDecodeError as e:
            WS_LOGGER.error("JSON decode error: %s", e)
        except ValueError:
            await self._handle_invalid_message(message)
        except Exception as e:
            WS_LOGGER.error("Error processing message: %s", e)

    async def _execute_callback(self, callback: Callable[[Any], None] | Callable[[Any], Awaitable[None]], data: Any) -> None:
        if asyncio.iscoroutinefunction(callback):
            await callback(data)
        else:
            callback(data)

    async def _handle_invalid_message(self, message: str) -> None:
        if invalid_callback := self.callbacks.get(EventType.INVALID.value):
            await self._execute_callback(invalid_callback, message)
        else:
            WS_LOGGER.warning("Unrecognized WS Message: %s", message)

    async def _send(self, message: str) -> None:
        if self.websocket:
            await self.websocket.send(message)

    @staticmethod
    def _is_connected(websocket: websockets.WebSocketClientProtocol | None) -> bool:
        """Check if the websocket connection is open"""
        return websocket is not None and not websocket.closed

    def is_connected(self) -> bool:
        """Check if the websocket connection is open"""
        return self._is_connected(self.websocket) and not self._closing.is_set()

    async def close(self) -> None:
        """Close the WebSocket connection and stop the listening task."""
        WS_LOGGER.debug("Closing WebSocket connection")

        if self._closing.is_set():
            WS_LOGGER.debug("Close already in progress")
            await self._closed.wait()
            return

        self._closing.set()

        try:
            await self._send_stop_messages()
            await self._close_websocket()
            await self._wait_for_listen_task()
        finally:
            await self._closed.wait()
            WS_LOGGER.debug("WebSocket connection closed")

    async def _send_stop_messages(self) -> None:
        for device_id in self.device_ids:
            WS_LOGGER.debug("Unregistering Websocket Listener for device_id: %s", device_id)
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        self.send_message(ListenStopMessage(device_id=device_id)),
                        self.send_message(RapidWindListenStopMessage(device_id=device_id))
                    ),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                WS_LOGGER.warning("Timeout sending stop messages for device_id: %s", device_id)
            except Exception as e:
                WS_LOGGER.error("Error sending stop messages for device_id %s: %s", device_id, e)

    async def _close_websocket(self) -> None:
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                WS_LOGGER.error("Error closing WebSocket: %s", e)
            finally:
                self.websocket = None

    async def _wait_for_listen_task(self) -> None:
        if self.listen_task:
            try:
                await asyncio.wait_for(self.listen_task, timeout=5.0)
            except asyncio.TimeoutError:
                WS_LOGGER.warning("Timeout waiting for listen task to complete")
            except Exception as e:
                WS_LOGGER.error("Error waiting for listen task to complete: %s", e)
            finally:
                self.listen_task = None