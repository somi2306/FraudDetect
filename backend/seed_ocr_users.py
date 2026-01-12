import os
import asyncio
import glob
import random
import string
import sys
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from urllib.parse import quote_plus

# --- 1. CONFIGURATION ---
load_dotenv()
sys.path.append(os.getcwd())

from app.models.user import User, UserRole
from app.models.bank import Bank  # <--- AJOUT IMPORTANT
from app.services.cheque_reader import correct_beneficiary_name, detect_and_read_cheque_zones
from app.services.clerk_service import create_clerk_user, delete_clerk_user, CLERK_SECRET_KEY
from app.utils.bank_codes import get_bank_id_from_code, BANK_CODE_TO_ID
from app.models.cheque import Cheque
from app.models.details_cheque import DetailsCheque
USER = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")

encoded_password = quote_plus(PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{encoded_password}@{HOST}:{PORT}/{NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

PUBLIC_FOLDER = "public"

# --- 2. UTILITAIRES ---

def clean_str(s):
    return "".join(c for c in s if c.isalnum()).lower()

def generate_random_cin():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=6))
    return f"{letters}{numbers}"

def generate_random_rib(bank_code):
    suffix = ''.join(random.choices(string.digits, k=21))
    return f"{bank_code}{suffix}"

# --- 3. LOGIQUE DE NETTOYAGE ---

async def cleanup_existing_test_users(session: Session):
    print("\n🧹 --- DÉMARRAGE DU NETTOYAGE ---")
    
    # Récupérer les utilisateurs de test
    users_to_delete = session.query(User).filter(User.email.like("%@test.com")).all()
    
    if not users_to_delete:
        print("✅ Aucun utilisateur de test trouvé à nettoyer.")
        return

    print(f"⚠️ {len(users_to_delete)} utilisateurs trouvés à supprimer...")

    for user in users_to_delete:
        print(f"   🗑️ Suppression de {user.email}...")

        # --- NOUVEAU : SUPPRESSION DES DÉPENDANCES ---
        
        # 1. Récupérer tous les chèques de cet utilisateur
        user_cheques = session.query(Cheque).filter(Cheque.beneficiaire_id == user.id).all()
        
        for cheque in user_cheques:
            # 2. Supprimer les détails du chèque (s'ils existent)
            session.query(DetailsCheque).filter(DetailsCheque.cheque_id == cheque.id).delete()
            
            # 3. Supprimer le chèque lui-même
            session.delete(cheque)
        
        # ---------------------------------------------

        # 4. Suppression de Clerk
        if user.clerk_id:
            try:
                await delete_clerk_user(user.clerk_id)
            except Exception as e:
                # On ignore si l'user Clerk n'existe déjà plus
                pass 
        
        # 5. Suppression de l'utilisateur en DB locale
        session.delete(user)
    
    session.commit()
    print("✨ Nettoyage terminé ! Base de données propre pour les tests.\n")


# --- 4. CRÉATION AVEC BANQUE ALÉATOIRE ---

async def create_user_from_cheque(file_path, session, all_banks):
    """
    all_banks: liste des objets Bank disponibles en DB
    """
    filename = os.path.basename(file_path)
    print(f"📸 Traitement : {filename}")

    # OCR (On le garde pour extraire le nom du bénéficiaire sur l'image)
    result = detect_and_read_cheque_zones(file_path)
    data = result.get("data", {}) if result.get("status") == "SUCCESS" else {}
    
    beneficiaire_text = data.get("Beneficiaire", {}).get("text", "").strip()
    beneficiaire_text = correct_beneficiary_name(beneficiaire_text)
    # Si OCR échoue sur le nom, on invente
    if not beneficiaire_text or len(beneficiaire_text) < 3:
        beneficiaire_text = "User Test " + "".join(random.choices(string.ascii_uppercase, k=3))

    # --- CHANGEMENT DE LOGIQUE ICI ---
    
    # 1. On ignore la banque détectée sur le chèque pour l'assignation du User
    # On choisit une banque ALÉATOIRE parmi celles existantes en base
    if not all_banks:
        print("❌ CRITIQUE : Aucune banque trouvée en base de données.")
        return

    random_bank = random.choice(all_banks)
    
    # L'ID de banque du bénéficiaire sera celui choisi au hasard
    beneficiaire_bank_id = random_bank.id
    
    # Le RIB du bénéficiaire doit correspondre à SA banque (et pas celle du chèque)
    # On cherche le code banque correspondant (ex: '190' pour CIH, '181' pour BCP...)
    # On suppose ici que tu as un moyen de trouver le code via BANK_CODE_TO_ID inversé 
    # ou que tu as stocké le code dans la table Bank. 
    # Pour faire simple, on génère un RIB générique, mais le bank_id est le plus important.
    
    # Tentative de retrouver le code banque via le nom ou l'ID si possible, sinon random
    beneficiaire_rib = generate_random_rib("111") # Code par défaut si inconnu
    
    # Si tu as stocké le code dans ton modèle Bank, utilise : random_bank.code
    # Sinon on essaie de deviner via ton dictionnaire existant :
    for code, b_id in BANK_CODE_TO_ID.items():
        if b_id == beneficiaire_bank_id:
            beneficiaire_rib = generate_random_rib(code)
            break

    # Infos User
    parts = beneficiaire_text.split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = " ".join(parts[1:])
    else:
        first_name = beneficiaire_text
        last_name = "Test"

    clean_first = clean_str(first_name) or "user"
    clean_last = clean_str(last_name) or "test"
    # Ajout d'un random pour éviter les doublons d'email si le même nom revient
    rand_suffix = "".join(random.choices(string.digits, k=4))
    fake_email = f"{clean_first}.{clean_last}{rand_suffix}@test.com"
    user_password = f"{clean_first}_{clean_last}123456789"
    cin_aleatoire = generate_random_cin()

    # Création Clerk
    clerk_id = None
    clerk_image_url = ""
    
    try:
        clerk_response = await create_clerk_user(
            email=fake_email,
            password=user_password,
            first_name=first_name,
            last_name=last_name
        )
        clerk_id = clerk_response.get("id")
        clerk_image_url = clerk_response.get("image_url")
    except Exception as e:
        print(f"   ❌ Erreur Clerk ({fake_email}): {e}")
        return

    # Sauvegarde DB
    try:
        new_user = User(
            clerk_id=clerk_id,
            email=fake_email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.BENEFICIAIRE,
            is_active=True,
            must_reset_password=False,
            personal_email=fake_email,
            cin=cin_aleatoire,
            rib=beneficiaire_rib,   # RIB cohérent avec la banque aléatoire
            bank_id=beneficiaire_bank_id, # Banque aléatoire
            image_url=clerk_image_url
        )
        session.add(new_user)
        session.commit()
        print(f"   ✅ Créé: {fake_email} -> Banque ID: {beneficiaire_bank_id}")

    except Exception as e:
        session.rollback()
        print(f"   ❌ Erreur DB: {e}")


async def main():
    # 1. Nettoyage
    with Session(engine) as session:
        await cleanup_existing_test_users(session)

        # 2. Récupérer toutes les banques UNE SEULE FOIS
        all_banks = session.query(Bank).all()
        print(f"🏦 {len(all_banks)} banques disponibles pour l'assignation aléatoire.")

        # 3. Collecte fichiers
        files = []
        extensions = ["*.png", "*.jpg", "*.jpeg"]
        for ext in extensions:
            files.extend(glob.glob(os.path.join(PUBLIC_FOLDER, ext)))
            files.extend(glob.glob(os.path.join(PUBLIC_FOLDER, "**", ext), recursive=True))
        files = sorted(list(set([f for f in files if "node_modules" not in f])))

        print(f"📂 {len(files)} images trouvées. Création des users avec banques mixtes...\n")

        # 4. Création
        for file_path in files:
            # On passe la liste des banques à la fonction
            await create_user_from_cheque(file_path, session, all_banks)

if __name__ == "__main__":
    asyncio.run(main())