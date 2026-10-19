import asyncio
import json
from websockets.asyncio.server import serve

clients = set()


async def handler(ws):
    clients.add(ws)
    print("Node.js connected")

    try:
        async for raw in ws:
            data = json.loads(raw)

            # Messages arriving from Node.js
            if data.get("type") == "whatsapp.incoming":
                print("WhatsApp:", data)

                # TODO: Forward data to your assistant/LLM
                await send_to_node({
                    "type": "whatsapp.send",
                    "chatId": data["chatId"],
                    "text": data["text"]
                })

            # Example response/command from Node.js
            elif data.get("type") == "bridge.status":
                print(data)

    finally:
        clients.discard(ws)


async def send_to_node(data):
    """Send a command to the connected Node.js bridge."""
    if not clients:
        print("Node.js is not connected")
        return

    message = json.dumps(data)
    await asyncio.gather(
        *(ws.send(message) for ws in list(clients)),
        return_exceptions=True,
    )


async def main():
    async with serve(handler, "127.0.0.1", 8765):
        print("MCP bridge listening on ws://127.0.0.1:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
