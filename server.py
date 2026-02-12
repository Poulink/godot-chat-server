import asyncio
import os
import websockets

clients = set()

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            for client in clients:
                await client.send(message)
    finally:
        clients.remove(websocket)


# 👇 Вот это решает проблему HEAD запросов Render
async def process_request(path, request_headers):
    if request_headers.get("Method", "") == "HEAD":
        return (
            200,
            [("Content-Type", "text/plain")],
            b"OK",
        )


async def main():
    port = int(os.environ.get("PORT", 10000))

    async with websockets.serve(
        handler,
        "0.0.0.0",
        port,
        process_request=process_request
    ):
        print("Server started")
        await asyncio.Future()  # работает вечно


asyncio.run(main())
