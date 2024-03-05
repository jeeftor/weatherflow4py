import asyncio
import os

from dotenv import load_dotenv

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage,
    RapidWindListenStartMessage,
)
from weatherflow4py.models.ws.websocket_response import (
    RapidWindWS,
    ObservationTempestWS,
)
from weatherflow4py.ws import WebsocketAPI

import logging

logging.basicConfig(level=logging.INFO)


def invalid_data_cb(data):
    print("Invalid data ❗️ received:", data)


def wind_cb(data: RapidWindWS):
    print("Wind 🍃 data received:", data)


def obs_cb(data: ObservationTempestWS):
    print("Observation 🔎️ data received:", data)


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")

    api = WebsocketAPI(device, token)
    api._register_callback(EventType.INVALID, invalid_data_cb)
    api.register_observation_callback(obs_cb)
    # api.register_wind_callback(wind_cb)

    await api.connect()
    await api.send_message(ListenStartMessage(device_id=device))
    await api.send_message(RapidWindListenStartMessage(device_id=device))

    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    # print(api.listen_task)
    #
    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    # print(api.listen_task)
    #
    # await asyncio.sleep(30)
    #
    # print("DATA::", api.messages)
    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    # await asyncio.sleep(30)
    # print("DATA::", api.messages)
    #
    # await asyncio.sleep(120)

    await asyncio.sleep(30000)
    await api.close()


if __name__ == "__main__":
    asyncio.run(main())
