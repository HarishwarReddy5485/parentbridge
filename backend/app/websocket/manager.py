from collections import defaultdict
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps conversation_id -> set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id].add(websocket)

    def disconnect(self, conversation_id: str, websocket: WebSocket):
        self.active_connections[conversation_id].discard(websocket)
        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: str, payload: dict):
        if conversation_id in self.active_connections:
            for connection in list(self.active_connections[conversation_id]):
                try:
                    await connection.send_json(payload)
                except Exception:
                    self.disconnect(conversation_id, connection)


manager = ConnectionManager()
