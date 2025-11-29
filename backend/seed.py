# backend/seed.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from urllib.parse import quote_plus
import enum # Ajout de l'import enum si nécessaire

# --- Charger les variables d'environnement ---
load_dotenv()

USER = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")

# --- Construction de l'URL de connexion PostgreSQL ---
encoded_password = quote_plus(PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{encoded_password}@{HOST}:{PORT}/{NAME}"

# --- Imports de vos modèles ---
from app.models.bank import Bank 
from app.models.user import User 

# Définition des rôles (Assurez-vous que cette définition correspond à celle dans app.models.user)
class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    AGENT = "Agent"
    BENEFICIAIRE = "Bénéficiaire"

# --- Configuration et Connexion ---
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'options': '-csearch_path=public'})

# --- Données à insérer ---
# Utilisez le mot de passe haché généré pour 'Agent123'
HASHED_PASSWORD = "$5$rounds=535000$jjPvEKLkxVZTi38Y$pSM2t2viVsO4S9EC1SNouxAsSYD6QAKGKY8xTJQJYr6" 

# Liste des banques
BANKS_DATA = [
    {"name": "CIH Banque"},
    {"name": "Attijariwafa Banque"},
    {"name": "Banque Populaire"},
]

# Liste des agents avec leur bank_id (qui correspondra à l'ID généré après insertion)
AGENTS_DATA = [
    {"email": "agent1@fraud.com", "first_name": "Agent", "last_name": "Un", "bank_id": 1},
    {"email": "agent2@fraud.com", "first_name": "Alya", "last_name": "Benali", "bank_id": 2},
    {"email": "agent3@fraud.com", "first_name": "Karim", "last_name": "Hassani", "bank_id": 2},
    {"email": "agent4@fraud.com", "first_name": "Sarah", "last_name": "Lalami", "bank_id": 3},
]


def seed_database():
    with Session(engine) as session:
        
        # 0. Nettoyage initial : Suppression COMPLÈTE des Banques et Agents
        print("0. Suppression des Agents et Banques existantes...")
        session.query(User).delete()  # Supprimer les dépendants d'abord
        session.query(Bank).delete()  # Puis supprimer la cible
        session.commit()
        
        # 1. Insertion des banques (LOGIQUE RESTAURÉE)
        print("1. Insertion des Banques...")
        
        bank_objects = []
        for data in BANKS_DATA:
            bank = Bank(**data)
            bank_objects.append(bank)
            session.add(bank)
        
        session.commit()
        
        # 1. BIS. Récupération des IDs réels insérés
        inserted_banks = session.query(Bank).all()
        bank_map = {bank.name: bank.id for bank in inserted_banks}
        print(f"Banques insérées (et leurs IDs) : {bank_map}") 
        
        # 2. Insertion des agents
        print("2. Insertion des Agents...")
        
        # Pour une base de données fraîchement nettoyée et insérée, les IDs seront 1, 2, 3.
        # On utilise une carte Nom -> ID pour s'assurer que l'ID utilisé dans AGENTS_DATA est valide.
        name_to_id = {bank.name: bank.id for bank in inserted_banks}
        
        for data in AGENTS_DATA:
            
            user_data = data.copy()
            user_data.pop('bank_id') # Retrait de l'ancienne valeur 'bank_id' (1, 2, 3)
            
            # Récupère le nom de la banque à partir de la liste BANKS_DATA en utilisant le bank_id (ex: 1 -> CIH Banque)
            bank_name_from_data = BANKS_DATA[data['bank_id'] - 1]['name']
            
            # Obtient l'ID réel inséré dans la base de données (ex: 5, 6, 7)
            actual_bank_id = name_to_id.get(bank_name_from_data)
            
            if not actual_bank_id:
                print(f"⚠️ Avertissement : ID de banque {data['bank_id']} introuvable. Ignoré.")
                continue

            # Création de l'objet User (Agent)
            agent = User(
                **user_data, # <-- CORRECTION : Utilisez le dictionnaire sans 'bank_id'
                role=UserRole.AGENT, 
                hashed_password=HASHED_PASSWORD,
                must_reset_password=True,
                bank_id=actual_bank_id # <-- Passe la VRAIE valeur une seule fois
            )
            session.add(agent)
            
        session.commit()
        print("✅ Agents insérés avec succès !")
if __name__ == "__main__":
    seed_database()