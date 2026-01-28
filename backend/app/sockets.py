from fastapi import WebSocket
from typing import List
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)
        print(f"✅ New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_progress(self, data: dict):
        """Send progress update to all clients"""
        if not self.active_connections:
            return
        
        # Convert to JSON string once
        import json
        message = json.dumps(data)
        
        # Send to all connections
        disconnected = []
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Failed to send to client: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

# Global manager instance
manager = ConnectionManager()

async def connect(websocket: WebSocket):
    await manager.connect(websocket)

async def broadcast_progress(data: dict):
    """Public function to broadcast progress"""
    await manager.send_progress(data)