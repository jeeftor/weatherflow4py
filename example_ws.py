import asyncio
import os

from dotenv import load_dotenv

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage,
    RapidWindListenStartMessage,
)
from weatherflow4py.ws import WebsocketAPI

import logging

logging.basicConfig(level=logging.DEBUG)


def invalid_data_cb(data):
    print("Invalid data received:", data)


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")
    # Replace 'your_device_id' and 'your_access_token' with your actual Device ID and Access Token
    # asyncio.run(listen_to_tempest(device, token))
    # Send a message

    # Sleep for 2 minutes

    api = WebsocketAPI(device, token)

    api.register_callback(EventType.INVALID, invalid_data_cb)
    await api.connect()

    await api.send_message(ListenStartMessage(device_id=device))
    await api.send_message(RapidWindListenStartMessage(device_id=device))

    await asyncio.sleep(1)

    print(api.listen_task)

    await asyncio.sleep(30)
    print("DATA::", api.messages)
    print(api.listen_task)

    await asyncio.sleep(30)
    print("DATA::", api.messages)
    print(api.listen_task)

    await asyncio.sleep(30)

    print("DATA::", api.messages)
    await asyncio.sleep(30)
    print("DATA::", api.messages)
    await asyncio.sleep(30)
    print("DATA::", api.messages)
    await asyncio.sleep(30)
    print("DATA::", api.messages)
    await asyncio.sleep(30)
    print("DATA::", api.messages)

    await asyncio.sleep(120)

    await api.close()


if __name__ == "__main__":
    asyncio.run(main())
