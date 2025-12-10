# backend/app/services/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Stocke les connexions : { agent_id: [WebSocket, WebSocket, ...] }
        # On utilise une liste car un agent peut être connecté sur plusieurs onglets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        self.active_connections[agent_id].append(websocket)
        print(f"🔌 Agent {agent_id} connecté via WebSocket.")

    def disconnect(self, websocket: WebSocket, agent_id: str):
        if agent_id in self.active_connections:
            if websocket in self.active_connections[agent_id]:
                self.active_connections[agent_id].remove(websocket)
            if not self.active_connections[agent_id]:
                del self.active_connections[agent_id]
        print(f"🔌 Agent {agent_id} déconnecté.")

    async def send_personal_message(self, message: dict, agent_id: str):
        """Envoie un message à un agent spécifique."""
        if agent_id in self.active_connections:
            for connection in self.active_connections[agent_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Erreur d'envoi WebSocket à {agent_id}: {e}")

    async def broadcast_to_bank(self, message: dict, bank_id: int, user_model):
        """
        Envoie un message à tous les agents d'une banque spécifique.
        Nécessite une requête DB pour trouver les IDs des agents de cette banque.
        """
        # Note: Pour éviter l'import circulaire, on passera la session DB depuis la route
        # Mais pour simplifier ici, on suppose qu'on cible par ID agent direct
        pass 

# Instance globale
manager = ConnectionManager()