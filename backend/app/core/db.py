# backend/app/core/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.pool import NullPool # <--- IMPORT AJOUTÉ
from urllib.parse import quote_plus 

# Lire l'URL de la DB depuis votre fichier .env
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Si les variables d'environnement ne sont pas toutes définies, on bascule
# automatiquement sur une base SQLite locale pour le développement.
if not all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    print("ATTENTION: Certaines variables d'environnement de la DB sont manquantes. Basculage en mode DEV (SQLite local).")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./dev.db"
    # Utilisation d'une base SQLite locale (développement). 
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        print(f"Tentative de connexion à SQLite locale: {SQLALCHEMY_DATABASE_URL}")
        with engine.connect() as conn:
            print("✅ Connexion à SQLite (développement) réussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion SQLite: {e}")
        engine = None
else:
    # Encoder le mot de passe s'il contient des caractères spéciaux
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Tentative de connexion à: postgresql://{DB_USERNAME}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        # --- CORRECTION ICI ---
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, 
            pool_pre_ping=True,
            poolclass=NullPool  # <--- DÉSACTIVE LE POOLING SQLALCHEMY (Vital pour Supabase)
        )
        # ----------------------
        
        # Tester la connexion
        with engine.connect() as conn:
            print("✅ Connexion à la base de données (SQLAlchemy) réussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion (SQLAlchemy): {e}")
        engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Définir la Base
class Base(DeclarativeBase):
    pass

def create_db_and_tables():
    if engine is None:
        print("❌ Impossible de créer les tables: moteur de base de données non disponible")
        return
    try:
        print("Création des tables (si elles n'existent pas)...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")

def get_db():
    if engine is None:
        raise Exception("Base de données non disponible")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()