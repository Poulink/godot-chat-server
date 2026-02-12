import asyncio
import os
from websockets.server import serve
from websockets.exceptions import ConnectionClosedOK

clients = set()

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            for client in clients:
                await client.send(message)
    except ConnectionClosedOK:
        pass
    finally:
        clients.remove(websocket)

async def health_check(reader, writer):
    request = await reader.read(1024)
    if b"HEAD" in request or b"GET / " in request:
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 2\r\n"
            "\r\nOK"
        )
        writer.write(response.encode())
        await writer.drain()
    writer.close()

async def main():
    port = int(os.environ.get("PORT", 10000))

    ws_server = await serve(handler, "0.0.0.0", port)
    http_server = await asyncio.start_server(health_check, "0.0.0.0", port)

    print("Server started")
    await asyncio.gather(ws_server.wait_closed(), http_server.serve_forever())

asyncio.run(main())

