# chat_client.py
import asyncio
import websockets

SERVER_URI = "ws://127.0.0.1:6789"

async def send_messages(ws, username, room):
    """Send user input to the server."""
    print("💬 You can start chatting! Type /quit to exit.")
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, "")
        if msg.lower() == "/quit":
            print("👋 Disconnecting...")
            await ws.close()
            break
        await ws.send(msg)


async def receive_messages(ws):
    """Receive and display messages from the server."""
    try:
        async for message in ws:
            print(message)
    except websockets.exceptions.ConnectionClosed:
        print("❌ Disconnected from server.")


async def main():
    username = input("Choose a username: ").strip()
    room = input("Room to join: ").strip()

    try:
        async with websockets.connect(SERVER_URI) as ws:
            # Send join info
            await ws.send(f"{username}:{room}")
            print(f"✅ Connected to room: {room}")

            # Run sender & receiver concurrently
            recv_task = asyncio.create_task(receive_messages(ws))
            send_task = asyncio.create_task(send_messages(ws, username, room))

            await asyncio.gather(recv_task, send_task)

    except ConnectionRefusedError:
        print("❌ Cannot connect to server. Is chat_server.py running?")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped.")
