import json
from typing import Any

from fastapi import WebSocket

from src.core.console import console


class WebSocketManager:
    def __init__(self):
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)
        console.log(f"[info]WS conectado: user {user_id}[/]")

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id] = [
                ws for ws in self._connections[user_id] if ws != websocket
            ]
            if not self._connections[user_id]:
                del self._connections[user_id]
        console.log(f"[info]WS desconectado: user {user_id}[/]")

    async def notify(self, user_id: int, payload: dict[str, Any]) -> None:
        connections = self._connections.get(user_id, [])
        message = json.dumps(payload)
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                await self.disconnect(user_id, ws)


ws_manager = WebSocketManager()
