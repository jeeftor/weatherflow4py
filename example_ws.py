import asyncio
import os

# from weatherflow4py.models.websocket_request import ResponseBuilder, Acknowledgement, RainStartEvent, LightningStrikeEvent, RapidWind, \
#     ObservationAir, ObservationSky, ObservationTempest

from dotenv import load_dotenv

from weatherflow4py.ws import WebsocketAPI


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

    api.register_callback(api.EventType.INVALID, invalid_data_cb)
    await api.connect()

    await api.send_message(api.MessageType.LISTEN_START)
    await api.send_message(api.MessageType.RAPID_WIND_START)

    await asyncio.sleep(1)
    print("Request winds")

    await asyncio.sleep(30)
    print("DATA::", api.messages)
    await asyncio.sleep(30)
    print("DATA::", api.messages)
    await asyncio.sleep(30)
    await api.send_message(api.MessageType.LISTEN_STOP)
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
