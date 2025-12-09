import httpx
import os

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_API_URL = "https://api.clerk.com/v1"

async def create_clerk_user(email: str, password: str, first_name: str, last_name: str):
    if not CLERK_SECRET_KEY:
        raise Exception("CLERK_SECRET_KEY manquant dans le .env")

    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email_address": [email],
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "skip_password_checks": False,
        "skip_password_requirement": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CLERK_API_URL}/users", json=payload, headers=headers)
        
        if response.status_code not in [200, 201]:
            # Gestion d'erreur améliorée pour lire le message de Clerk
            try:
                error_data = response.json()
                error_msg = error_data.get("errors", [{"message": "Erreur inconnue"}])[0]["message"]
            except:
                error_msg = response.text
            raise Exception(f"Erreur Clerk: {error_msg}")
            
        return response.json()
