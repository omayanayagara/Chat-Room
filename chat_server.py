import asyncio
import websockets
import json

rooms = {}  # { room_name: set of (websocket, username) }

async def handler(websocket):
    username = None
    room = None
    try:
        # First message must be join info
        join_data = await websocket.recv()
        data = json.loads(join_data)
        username = data["username"]
        room = data["room"]

        if room not in rooms:
            rooms[room] = set()
        rooms[room].add((websocket, username))

        # Notify in terminal
        print(f"🔵 {username} joined the chat in {room}")

        # Notify everyone in the room
        join_msg = f"🔵 {username} joined the chat"
        for ws, _ in rooms[room]:
            await ws.send(json.dumps({"text": join_msg}))

        # Confirm connection to the user
        await websocket.send(json.dumps({"text": f"✅ Connected to room: {room}"}))
        await websocket.send(json.dumps({"text": "💬 You can start chatting! Type /quit to exit."}))

        # Chat loop
        async for message in websocket:
            msg_data = json.loads(message)
            text = msg_data["text"]

            # Quit command
            if text.lower() == "/quit":
                await websocket.close()
                break

            chat_msg = f"{username}: {text}"
            print(chat_msg)
            for ws, _ in rooms[room]:
                await ws.send(json.dumps({"text": chat_msg}))

    except websockets.ConnectionClosed:
        pass
    finally:
        if room and username:
            rooms[room].discard((websocket, username))
            leave_msg = f"❌ {username} left the chat"
            print(leave_msg)
            for ws, _ in rooms[room]:
                await ws.send(json.dumps({"text": leave_msg}))

async def main():
    async with websockets.serve(handler, "localhost", 6789):
        print("✅ Server running on ws://localhost:6789")
        await asyncio.Future()

asyncio.run(main())
