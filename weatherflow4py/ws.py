from enum import Enum

import asyncio
import websockets
import json

from weatherflow4py.models.websocket_response import WebsocketResponseBuilder


class WebsocketAPI:
    def __init__(self, device_id: str, access_token: str):
        self.device_id = device_id
        self.uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
        self.websocket = None
        self.messages = []
        self.is_listening = False
        self.listen_task = None  # To keep track of the listening task

    class MessageType(Enum):
        LISTEN_START = "listen_start"
        LISTEN_STOP = "listen_stop"
        RAPID_WIND_START = "listen_rapid_start"
        RAPID_WIND_STOP = "listen_rapid_stop"

    async def send_message(self, message_type: MessageType):
        message = {
            "type": message_type.value,
            "device_id": self.device_id,
            "id": "unique_id_here",
        }
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
                data = json.loads(message)

                try:
                    response = WebsocketResponseBuilder.build_response(data)
                    print(message)
                    print(response)

                except ValueError:
                    print(f"INVALID:\n {message}")

                    continue

                print(data)  # Process the data as needed
                self.messages.append(data)
        finally:
            self.is_listening = False

    async def _send(self, message):
        if self.websocket:
            await self.websocket.send(json.dumps(message))

    def is_connected(self):
        # Check if the websocket connection is open
        return self.websocket and not self.websocket.closed

    async def close(self):
        await self.send_message(self.MessageType.LISTEN_STOP)
        await self.send_message(self.MessageType.RAPID_WIND_STOP)

        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.listen_task:
            self.listen_task.cancel()  # Cancel the listening task
            try:
                await self.listen_task  # Await the task to handle cancellation
            except asyncio.CancelledError:
                pass  # Task cancellation is expected
