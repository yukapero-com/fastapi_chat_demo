from typing import List

import json
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = "<h1>fastapi chat server demo</h1>"

messages = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.send_personal_message(json.dumps(messages), websocket)
    try:
        while True:
            data = await websocket.receive_text()
            dt_now = datetime.datetime.now()
            chatText = f"#{client_id} says: {data} ({dt_now})"
            messages.append(chatText)
            await manager.broadcast(chatText)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"#{client_id} left the room")
