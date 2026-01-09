import httpx
import os

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_API_URL = "https://api.clerk.com/v1"

# --- CORRECTION : HEADERS DÉFINIS GLOBALEMENT ---
# Ils sont maintenant visibles par TOUTES les fonctions du fichier
headers = {
    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
    "Content-Type": "application/json"
}

async def create_clerk_user(email: str, password: str, first_name: str, last_name: str):
    if not CLERK_SECRET_KEY:
        raise Exception("CLERK_SECRET_KEY manquant dans le .env")

    # (La variable headers n'est plus définie ici, elle utilise celle globale)

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
            try:
                error_data = response.json()
                error_msg = error_data.get("errors", [{"message": "Erreur inconnue"}])[0]["message"]
            except:
                error_msg = response.text
            raise Exception(f"Erreur Clerk: {error_msg}")
            
        return response.json()

async def update_clerk_user(user_id: str, first_name: str, last_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{CLERK_API_URL}/users/{user_id}",
            json={"first_name": first_name, "last_name": last_name},
            headers=headers # <--- Maintenant ça fonctionne !
        )
        if response.status_code != 200:
            raise Exception(f"Erreur Clerk Update ({response.status_code}): {response.text}")
        return response.json()

async def toggle_clerk_ban(user_id: str, ban: bool):
    url = f"{CLERK_API_URL}/users/{user_id}/{'ban' if ban else 'unban'}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Erreur Clerk Ban/Unban: {response.text}")
        return response.json()

async def set_clerk_password(user_id: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{CLERK_API_URL}/users/{user_id}",
            json={"password": password},
            headers=headers
        )

        if response.status_code != 200:
            try:
                print("Erreur Clerk Password:", response.json())
            except:
                print("Erreur Clerk Password:", response.text)

            raise Exception(f"[Clerk Password] {response.status_code} - {response.text}")

        return response.json()
