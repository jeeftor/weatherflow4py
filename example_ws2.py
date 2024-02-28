import asyncio
import os

import websockets
import json
from weatherflow4py.models.websocket_response import WebsocketResponseBuilder
from dotenv import load_dotenv


async def listen_to_tempest(device_id, access_token):
    uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"

    async with websockets.connect(uri) as websocket:
        # Start listening
        listen_start = {
            "type": "listen_start",
            "device_id": device_id,
            "id": "unique_id_here",  # Generate a unique ID for your request
        }
        await websocket.send(json.dumps(listen_start))

        # Handle incoming messages
        async for message in websocket:
            data = json.loads(message)
            #
            # Use the ResponseBuilder to create an instance of the appropriate response class
            try:
                response = WebsocketResponseBuilder.build_response(data)
                print(response)
            except ValueError:
                print(f"INVALID:\n {message}")

                continue

        # Stop listening (optional, depending on your application logic)
        listen_stop = {
            "type": "listen_stop",
            "device_id": device_id,
            "id": "unique_id_here",  # The same or another unique ID
        }
        await websocket.send(json.dumps(listen_stop))


def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")
    # Replace 'your_device_id' and 'your_access_token' with your actual Device ID and Access Token
    asyncio.run(listen_to_tempest(device, token))


if __name__ == "__main__":
    main()
