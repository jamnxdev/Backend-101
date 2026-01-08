import asyncio
import time
import uuid
from dataclasses import dataclass, field
import websockets

HEARTBEAT_INTERVAL = 10
HEARTBEAT_TIMEOUT = 30
HEARTBEAT_CHECK_INTERVAL = 1
SEND_QUEUE_SIZE = 50
HOST = "0.0.0.0"
PORT = 8765

@dataclass
class Client:
    id: str
    websocket: websockets.asyncio.server.WebSocketServerProtocol
    last_seen: float = field(default_factory=time.time)
    send_queue: asyncio.Queue = field(
        default_factory=lambda: asyncio.Queue(maxsize=SEND_QUEUE_SIZE)
    )
    alive: bool = True

clients: dict[str, Client] = {}
clients_lock = asyncio.Lock()

async def disconnect_client(client: Client):
    if not client.alive:
        return

    client.alive = False
    
    async with clients_lock:
        clients.pop(client.id, None)

    try:
        await client.websocket.close()
    except Exception:
        pass

    print(f"[DISCONNECT] Client {client.id} disconnected")

async def broadcast(message: str):
    async with clients_lock:
        for client in list(clients.values()):
            try:
                client.send_queue.put_nowait(message)
            except asyncio.QueueFull:
                print(f"[BACKPRESSURE] Client {client.id} removed")
                await disconnect_client(client)

async def receive_loop(client: Client):
    try:
        async for message in client.websocket:
            if message == "heartbeat":
                client.last_seen = time.time()
                continue

            await broadcast(f"{client.id}: {message}")
    except Exception:
        pass
    finally:
        await disconnect_client(client)

async def send_loop(client: Client):
    try:
        while True:
            message = await client.send_queue.get()
            await client.websocket.send(message)
    except Exception:
        pass
    finally:
        await disconnect_client(client)

async def heartbeat_monitor():
    while True:
        now = time.time()

        async with clients_lock:
            for client in list(clients.values()):
                if now - client.last_seen > HEARTBEAT_TIMEOUT:
                    print(f"[TIMEOUT] {client.id}")
                    await disconnect_client(client)

            await asyncio.sleep(HEARTBEAT_CHECK_INTERVAL)

async def handler(websocket):
    client_id = str(uuid.uuid4())[:8]
    client = Client(id=client_id, websocket=websocket)

    async with clients_lock:
        clients[client.id] = client

    print(f"[CONNECTED] Client {client.id}")

    receiver = asyncio.create_task(receive_loop(client))
    sender = asyncio.create_task(send_loop(client))

    done, pending = await asyncio.wait(
        [receiver, sender],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

async def main():
    print(f"Server running on ws://{HOST}:{PORT}")

    async with websockets.serve(handler, HOST, PORT):
        await heartbeat_monitor()

if __name__ == "__main__":
    asyncio.run(main())