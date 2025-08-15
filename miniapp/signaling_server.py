import asyncio
import websockets
import json
import os  # добавлено для работы с переменными окружения

# Словарь: session_id -> set of websockets
sessions = {}

async def handler(websocket):
    session_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'join':
                session_id = data['session']
                if session_id not in sessions:
                    sessions[session_id] = set()
                sessions[session_id].add(websocket)
            elif data['type'] in ('offer', 'answer', 'ice'):
                # Пересылаем всем, кроме отправителя
                for ws in sessions.get(session_id, set()):
                    if ws != websocket:
                        await ws.send(message)
    finally:
        if session_id and websocket in sessions.get(session_id, set()):
            sessions[session_id].remove(websocket)
            if not sessions[session_id]:
                del sessions[session_id]

if __name__ == "__main__":
    async def main():
        port = int(os.environ.get("PORT", 8765))  # используем порт из переменной окружения
        async with websockets.serve(handler, "0.0.0.0", port):
            print(f"Signaling server started on ws://0.0.0.0:{port}")
            await asyncio.Future()  # run forever
    asyncio.run(main())