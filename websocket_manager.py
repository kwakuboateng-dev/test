from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # Store active connections: {match_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, match_id: int):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        
        self.active_connections[match_id].append(websocket)
        print(f"✅ WebSocket connected for match {match_id}")
    
    def disconnect(self, websocket: WebSocket, match_id: int):
        """Remove WebSocket connection"""
        if match_id in self.active_connections:
            self.active_connections[match_id].remove(websocket)
            
            # Clean up empty lists
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
        
        print(f"❌ WebSocket disconnected for match {match_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)
    
    async def broadcast_to_match(self, message: dict, match_id: int):
        """Send message to all connections in a match"""
        if match_id in self.active_connections:
            message_json = json.dumps(message)
            
            # Send to all connected clients in this match
            disconnected = []
            for connection in self.active_connections[match_id]:
                try:
                    await connection.send_text(message_json)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn, match_id)

# Global connection manager instance
manager = ConnectionManager()
