from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..services.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(websocket, agent_id)
    try:
        while True:
            # On garde la connexion ouverte.
            # On peut recevoir des "pings" du client pour dire "je suis là"
            data = await websocket.receive_text()
            # Pour l'instant, on ne fait rien des messages reçus du client
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)