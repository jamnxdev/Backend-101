import asyncio
import websockets
import sys

SERVER_URL = "ws://0.0.0.0:8765"
HEARBEAT_INTERVAL = 10

async def heartbeat(ws):
    while True:
        await asyncio.sleep(HEARBEAT_INTERVAL)
        await ws.send("heartbeat")

async def sender(ws):
    loop = asyncio.get_event_loop()

    while True:
        message = await loop.run_in_executor(None, sys.stdin.readline)
        await ws.send(message.strip())

async def receiver(ws):
    async for message in ws:
        print(message)

async def main():
    async with websockets.connect(SERVER_URL) as ws:
        print("Connected to serve")

        await asyncio.gather(
            heartbeat(ws),
            sender(ws),
            receiver(ws),
        )

if __name__ == "__main__":
    asyncio.run(main())