# backend/app/core/auth.py
import os
from fastapi import Request, HTTPException, status
from clerk_backend_api import Clerk, AuthenticateRequestOptions

# --- SECTION SÉCURITÉ AVEC clerk_backend_api ---
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
if not CLERK_SECRET_KEY:
    raise EnvironmentError("CLERK_SECRET_KEY est manquante dans .env")

# Initialisation du client Clerk
clerk_sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)

async def get_current_user(request: Request) -> dict:
    """
    Dépendance FastAPI pour valider le token avec clerk_backend_api
    """
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions()
        )

        if not request_state.is_signed_in:
            raise HTTPException(status_code=401, detail="Non authentifié")

        user_id = request_state.payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="ID utilisateur manquant")

        return {"user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur d'authentification Clerk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'authentification: {str(e)}",
        )