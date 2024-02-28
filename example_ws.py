import asyncio
import os

# from weatherflow4py.models.websocket_request import ResponseBuilder, Acknowledgement, RainStartEvent, LightningStrikeEvent, RapidWind, \
#     ObservationAir, ObservationSky, ObservationTempest

from dotenv import load_dotenv

from weatherflow4py.ws import WebsocketAPI


#
#
# async def listen_to_tempest(device_id, access_token):
#     uri = f"wss://ws.weatherflow.com/swd/data?token={access_token}"
#
#     async with websockets.connect(uri) as websocket:
#         # Start listening
#         listen_start = {
#             "type": "listen_start",
#             "device_id": device_id,
#             "id": "unique_id_here",  # Generate a unique ID for your request
#         }
#         await websocket.send(json.dumps(listen_start))
#
#         # Handle incoming messages
#         async for message in websocket:
#             data = json.loads(message)
#
#             try:
#                 response = WebsocketResponseBuilder.build_response(data)
#                 print(response)
#             except ValueError:
#                 print(f"INVALID:\n {message}")
#                 continue
#             # Example stop condition: stop after receiving a certain message
#             # if some_condition:
#             #     break
#
#         # Stop listening (optional, depending on your application logic)
#         listen_stop = {
#             "type": "listen_stop",
#             "device_id": device_id,
#             "id": "unique_id_here",  # The same or another unique ID
#         }
#         await websocket.send(json.dumps(listen_stop))


async def main():
    load_dotenv()  # load environment variables from .env file

    token = os.getenv("TOKEN")
    device = os.getenv("DEVICE")
    # Replace 'your_device_id' and 'your_access_token' with your actual Device ID and Access Token
    # asyncio.run(listen_to_tempest(device, token))
    # Send a message

    # Sleep for 2 minutes

    api = WebsocketAPI(device, token)
    await api.connect()

    await api.send_message(api.MessageType.LISTEN_START)
    await api.send_message(api.MessageType.RAPID_WIND_START)

    await asyncio.sleep(1)
    print("Request winds")

    await asyncio.sleep(120)

    if api.is_connected():
        print("WebSocket is connected.")

    if api.is_listening:
        print("WebSocket is listening for messages.")

    await asyncio.sleep(120)
    if api.is_connected():
        print("WebSocket is connected.")

    if api.is_listening:
        print("WebSocket is listening for messages.")

    await asyncio.sleep(120)

    await api.close()


if __name__ == "__main__":
    asyncio.run(main())
