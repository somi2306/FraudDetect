# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Chargement du .env (doit être appelé avant d'importer les modules qui lisent les variables) ---
load_dotenv()
from app.models import user, bank, cheque


# Imports de la logique de l'application
from .core.db import create_db_and_tables
from .routes import auth, users  # corrected: package is `routes`, not `routers`
from .routes import agents

# --- Initialisation de l'App ---
app = FastAPI()

# --- Ajout du Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Événement de démarrage ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- INCLURE LES ROUTEURS ---
# Inclut toutes les routes définies dans auth.py avec leur préfixe
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# Inclut toutes les routes définies dans users.py
app.include_router(users.router, prefix="/auth", tags=["Users"])
#le route de l'agent
app.include_router(agents.router, prefix="/agents", tags=["Agents Authentication"])


# --- Route Publique (peut rester ici ou aller dans son propre routeur) ---
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FraudDetect (Publique)"}
