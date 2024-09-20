import asyncio
import os
from collections import Counter
from dotenv import load_dotenv

from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage,
    RapidWindListenStartMessage,
)
from weatherflow4py.models.ws.websocket_response import (
    RapidWindWS,
    ObservationTempestWS,
)
from weatherflow4py.ws import WeatherFlowWebsocketAPI
import logging
from pprint import pprint

NUMBER_OF_MESSAGES = 5
REQUIRED_MESSAGE_TYPES = {"obs_st", "rapid_wind"}

ws_logger = logging.getLogger("websockets.client")
ws_logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

message_counter = Counter()
received_message_types = set()


def invalid_data_cb(data):
    print("Invalid data ❗️ received:", data)


def wind_cb(data: RapidWindWS):
    print("Wind 🍃 data received:", data)
    message_counter["rapid_wind"] += 1
    received_message_types.add("rapid_wind")
    print_message_count()


def obs_cb(data: ObservationTempestWS):
    print("Observation 🔎️ received")
    message_counter["obs_st"] += 1
    received_message_types.add("obs_st")
    print_message_count()


def print_message_count():
    total_messages = sum(message_counter.values())
    remaining = max(0, NUMBER_OF_MESSAGES - total_messages)
    print(
        f"Received {total_messages}/{NUMBER_OF_MESSAGES} messages. {remaining} remaining."
    )
    print(f"Message types received: {received_message_types}")


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")

    api = WeatherFlowWebsocketAPI(token, device)
    api.register_observation_callback(obs_cb)
    api.register_wind_callback(wind_cb)

    await api.connect()
    await api.send_message_and_wait(ListenStartMessage(device_id=device))
    await api.send_message_and_wait(RapidWindListenStartMessage(device_id=device))

    while sum(
        message_counter.values()
    ) < NUMBER_OF_MESSAGES or not REQUIRED_MESSAGE_TYPES.issubset(
        received_message_types
    ):
        await asyncio.sleep(1)

    print("-" * 80)
    await api.stop_all_listeners()
    print("-" * 80)
    # await api.send_message_and_wait(ListenStopMessage(device_id=device))
    # await api.send_message_and_wait(RapidWindListenStopMessage(device_id=device))

    print("Received all required message types and reached message limit.")
    print("Final message count:")
    pprint(dict(message_counter))
    print("DATA::")
    pprint(api.messages)

    # await api.close()
    print("Connection closed.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    finally:
        pending = asyncio.all_tasks(loop=loop)
        try:
            loop.run_until_complete(
                asyncio.wait_for(
                    asyncio.gather(*pending, return_exceptions=True), timeout=10
                )
            )
        except asyncio.TimeoutError:
            logger.warning("Listen task cancellation timed out or was cancelled")

        # Keep the loop running until Ctrl+C is hit
        try:
            while True:
                loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Exiting...")
        finally:
            loop.close()
