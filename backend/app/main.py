# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Chargement du .env ---
load_dotenv()
from app.models import user, bank, cheque


# Imports de la logique de l'application
from .core.db import create_db_and_tables
# AJOUTEZ L'IMPORT DE 'admin' ICI
from .routes import auth, users, agents, admin 

# --- Initialisation de l'App ---
app = FastAPI()

# --- Ajout du Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"], # Ajoutez vos ports frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Événement de démarrage ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- INCLURE LES ROUTEURS ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"]) # J'ai corrigé le préfixe /users ici (c'était /auth par erreur dans votre code)
app.include_router(agents.router, prefix="/agents", tags=["Agents Management"])

# AJOUTEZ CETTE LIGNE POUR ACTIVER LES ROUTES ADMIN
app.include_router(admin.router, prefix="/admin", tags=["Admin Management"])


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FraudDetect (Publique)"}
