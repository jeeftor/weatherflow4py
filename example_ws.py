import asyncio
import os

from dotenv import load_dotenv

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage, RapidWindListenStartMessage,
)
from weatherflow4py.models.ws.websocket_response import (
    RapidWindWS,
    ObservationTempestWS,
)
from weatherflow4py.ws import WeatherFlowWebsocketAPI

import logging
from pprint import pprint

ws_logger = logging.getLogger("websockets.client")
ws_logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.DEBUG)


def invalid_data_cb(data):
    print("Invalid data ❗️ received:", data)

def wind_cb(data: RapidWindWS):
    print("Wind 🍃 data received:", data)

def obs_cb(data: ObservationTempestWS):
    print("Observation 🔎️")  # data received:", data)


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")

    api = WeatherFlowWebsocketAPI(token, device)
    # api._register_callback(EventType.INVALID, invalid_data_cb)
    api.register_observation_callback(obs_cb)
    api.register_wind_callback(wind_cb)

    await api.connect()
    await api.send_message(ListenStartMessage(device_id=device))
    await api.send_message(RapidWindListenStartMessage(device_id=device))

    while True:
        await asyncio.sleep(120)
        print("DATA::", api.messages)
        pprint(api.messages)
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

    await asyncio.sleep(30000000000000)
    await api.close()


if __name__ == "__main__":
    asyncio.run(main())
