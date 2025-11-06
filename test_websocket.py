import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/face/recognize_realtime"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print("Received:", data)
        except KeyboardInterrupt:
            print("Disconnected")

if __name__ == "__main__":
    asyncio.run(test_websocket())
