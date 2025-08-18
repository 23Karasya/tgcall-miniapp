

import json
import os
from aiohttp import web

# Словарь: session_id -> set of websockets
sessions = {}

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    session_id = None
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data['type'] == 'join':
                    session_id = data['session']
                    if session_id not in sessions:
                        sessions[session_id] = set()
                    sessions[session_id].add(ws)
                elif data['type'] in ('offer', 'answer', 'ice'):
                    for peer in sessions.get(session_id, set()):
                        if peer != ws:
                            await peer.send_str(msg.data)
    finally:
        if session_id and ws in sessions.get(session_id, set()):
            sessions[session_id].remove(ws)
            if not sessions[session_id]:
                del sessions[session_id]
    return ws

async def healthcheck(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/", healthcheck)
app.router.add_get("/ws", websocket_handler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    web.run_app(app, host="0.0.0.0", port=port)