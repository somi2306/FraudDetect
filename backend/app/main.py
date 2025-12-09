from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Chargement du .env ---
load_dotenv()

# Imports de la logique de l'application
from app.core.db import create_db_and_tables

# --- IMPORT UNIFIÉ DES ROUTES ---
# On combine les routes de votre travail (Admin/Agent) et de l'autre branche (Bénéficiaire/Webhooks)
from app.routes import auth, users, agents, admin, checks, cheques, webhooks

# --- Initialisation de l'App ---
app = FastAPI()

# --- Ajout du Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"], # Supporte les deux ports fréquents
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Événement de démarrage ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- INCLURE LES ROUTEURS ---

# 1. Authentification
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 2. Gestion des Utilisateurs (Correction du préfixe appliquée)
app.include_router(users.router, prefix="/users", tags=["Users"])

# 3. Espace Admin (Votre fonctionnalité)
app.include_router(admin.router, prefix="/admin", tags=["Admin Management"])

# 4. Espace Agent (Votre fonctionnalité)
app.include_router(agents.router, prefix="/agents", tags=["Agents Management"])

# 5. Espace Bénéficiaire (Fonctionnalité fusionnée)
# Permet la gestion des remises de chèques
app.include_router(checks.router, tags=["Checks"]) 

# 6. Données Chèques Réels (Supabase)
app.include_router(cheques.router, prefix="/cheques", tags=["Cheques"])

# 7. Webhooks (Pour la synchro Clerk automatique)
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# --- Route Publique ---
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FraudDetect (Version Unifiée)"}