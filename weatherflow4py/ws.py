import asyncio
import websockets
import json


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
            print(data)  # Process the data as needed

            # Example stop condition: stop after receiving a certain message
            # if some_condition:
            #     break

        # Stop listening (optional, depending on your application logic)
        listen_stop = {
            "type": "listen_stop",
            "device_id": device_id,
            "id": "unique_id_here",  # The same or another unique ID
        }
        await websocket.send(json.dumps(listen_stop))


# Replace 'your_device_id' and 'your_access_token' with your actual Device ID and Access Token
asyncio.run(listen_to_tempest("your_device_id", "your_access_token"))
