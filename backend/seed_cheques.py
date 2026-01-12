import os
import glob
import sys
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from urllib.parse import quote_plus

# --- 1. CONFIGURATION ---
load_dotenv()
sys.path.append(os.getcwd())

# Import des modèles
from app.models.user import User, UserRole # Assurez-vous d'avoir UserRole si vous l'utilisez
from app.models.cheque import Cheque, CheckStatus
from app.models.details_cheque import DetailsCheque

from app.services.cheque_reader import detect_and_read_cheque_zones
from app.utils.bank_codes import get_bank_id_from_code, BANK_CODE_TO_ID

# Config DB
USER = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")

encoded_password = quote_plus(PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{encoded_password}@{HOST}:{PORT}/{NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

PUBLIC_FOLDER = "public"

# --- 2. FONCTIONS UTILITAIRES ---

def clean_amount(text):
    """Nettoie le montant (ex: '412.00' -> 412.0)"""
    if not text: return 0.0
    clean = text.replace(" ", "").replace(",", ".")
    clean = "".join(c for c in clean if c.isdigit() or c == ".")
    try:
        return float(clean)
    except:
        return 0.0

def parse_date(date_str):
    """
    Convertit une chaîne en objet datetime.
    """
    if not date_str:
        return datetime.now()

    clean_str = re.sub(r"[^0-9\-\/\.]", "", date_str).strip()
    
    formats = [
        "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", 
        "%Y-%m-%d", "%d-%m-%y", "%d/%m/%y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(clean_str, fmt)
        except ValueError:
            continue
            
    print(f"   ⚠️ Date illisible '{date_str}', utilisation de la date du jour.")
    return datetime.now()

def get_agent_for_bank(session, bank_id):
    """
    Récupère un agent appartenant à la banque spécifiée (celle du bénéficiaire).
    """
    try:
        # On cherche un agent qui a le même bank_id
        agent = session.query(User).filter(
            User.bank_id == bank_id,
            (User.role == 'AGENT') | (User.role == 'Agent') # Gestion majuscule/minuscule au cas où
        ).first()
        
        return agent.id if agent else None
    except Exception as e:
        print(f"   ⚠️ Erreur lors de la recherche de l'agent : {e}")
        return None

# --- 3. LOGIQUE PRINCIPALE ---

def seed_cheques():
    print("\n🏦 --- DÉMARRAGE DU SEEDING DES CHÈQUES ---")
    
    with Session(engine) as session:
        # 1. Nettoyage
        print("🧹 Nettoyage des chèques existants...")
        session.query(DetailsCheque).delete()
        session.query(Cheque).delete()
        session.commit()
        
        # 2. Récupération fichiers
        files = []
        extensions = ["*.png", "*.jpg", "*.jpeg"]
        for ext in extensions:
            files.extend(glob.glob(os.path.join(PUBLIC_FOLDER, ext)))
            files.extend(glob.glob(os.path.join(PUBLIC_FOLDER, "**", ext), recursive=True))
        files = sorted(list(set([f for f in files if "node_modules" not in f])))

        print(f"📂 {len(files)} images à traiter...")
        
        # 3. Traitement
        for file_path in files:
            filename = os.path.basename(file_path)
            print(f"\n📸 Traitement : {filename}")
            
            # > OCR
            result = detect_and_read_cheque_zones(file_path)
            if result.get("status") != "SUCCESS":
                print("   ❌ Erreur OCR. Ignoré.")
                continue
                
            data = result.get("data", {})
            
            # > Extraction
            benef_name = data.get("Beneficiaire", {}).get("text", "").strip()
            ocr_rib = data.get("Num_Compte", {}).get("text", "").replace(" ", "").replace("-", "")
            ocr_micr = data.get("Ligne_MICR", {}).get("text", "").replace(" ", "")
            montant_str = data.get("Montant_Chiffres", {}).get("text", "")
            montant_lettres = data.get("Montant_Lettres", {}).get("text", "")
            num_cheque = data.get("Num_Cheque", {}).get("text", "")
            date_emission_str = data.get("Date", {}).get("text", "")
            lieu = data.get("Lieu", {}).get("text", "")
            signature_b64 = data.get("Signature", {}).get("base64_image", "")

            if not benef_name:
                print("   ⚠️ Pas de bénéficiaire détecté. Ignoré.")
                continue

            # > 1. Trouver le USER (Bénéficiaire)
            parts = benef_name.split()
            if len(parts) >= 2:
                f_name = "".join(c for c in parts[0] if c.isalnum()).lower()
                l_name = "".join(c for c in " ".join(parts[1:]) if c.isalnum()).lower()
            else:
                f_name = "".join(c for c in benef_name if c.isalnum()).lower()
                l_name = "test"
            
            target_email = f"{f_name}.{l_name}@test.com"
            # Recherche partielle pour être plus souple (ex: user.test1234@test.com)
            user = session.query(User).filter(User.email.like(f"{f_name}.{l_name}%@test.com")).first()
            
            if not user:
                print(f"   ⚠️ Propriétaire introuvable ({target_email}). Skip.")
                continue
                
            # > 2. Trouver la BANQUE CIBLE (Celle du client / émetteur du chèque)
            # On se base sur le RIB ou le MICR du chèque
            target_bank_id = None
            detected_code = None
            
            if ocr_rib and len(ocr_rib) >= 3 and ocr_rib[:3] in BANK_CODE_TO_ID:
                detected_code = ocr_rib[:3]
            elif ocr_micr:
                for code in BANK_CODE_TO_ID.keys():
                    if code in ocr_micr:
                        detected_code = code
                        break
            
            if detected_code:
                try: 
                    target_bank_id = get_bank_id_from_code(detected_code)
                except: pass
            
            if not target_bank_id:
                # Fallback : Si on ne reconnait pas la banque du chèque, on met une ID par défaut (ex: 17)
                target_bank_id = 17 
            
            # > 3. Trouver l'AGENT (Même banque que le BÉNÉFICIAIRE)
            # C'est l'étape clé demandée : l'agent doit être de la même banque que le user qui dépose
            if not user.bank_id:
                 print(f"   ⚠️ L'utilisateur {user.email} n'a pas de banque assignée. Impossible d'assigner un agent.")
                 continue

            agent_id = get_agent_for_bank(session, user.bank_id)
            
            if not agent_id:
                print(f"   ⚠️ Aucun agent trouvé pour la banque {user.bank_id} (Banque du bénéficiaire).")
                # On peut décider de continuer sans agent (None) ou de skipper.
                # Ici on continue avec None, le chèque sera orphelin d'agent mais présent en base.
            
            # Gestion Image URL
            image_db_url = f"{filename}"

            # > 4. Créer CHEQUE
            new_cheque = Cheque(
                image_url=image_db_url,
                date_depot=datetime.now(),
                beneficiaire_id=user.id,
                banque_cible_id=target_bank_id, # Banque du client (RIB chèque)
                status=CheckStatus.PENDING,
                agent_actuel_id=agent_id        # Agent de la banque du bénéficiaire
            )
            session.add(new_cheque)
            session.flush()
            
            # > 5. Créer DETAILS
            final_date = parse_date(date_emission_str)

            detail = DetailsCheque(
                cheque_id=new_cheque.id,
                numero_cheque=num_cheque if num_cheque else "000000",
                montant_chiffre=clean_amount(montant_str),
                montant_lettre=montant_lettres,
                numero_compte=ocr_rib if ocr_rib else (user.rib if user.rib else "000000000000000000000000"),
                signature=signature_b64,
                lieu=lieu if lieu else "Inconnu",
                beneficiaire=benef_name,
                date_emission=final_date
            )
            session.add(detail)
            
            print(f"   ✅ OK -> Bénéficiaire: {user.email} (Banque {user.bank_id}) | Agent: {agent_id} | Cible: {target_bank_id}")
        
        session.commit()
        print("\n✨ Terminé ! Tous les chèques sont assignés correctement.")

if __name__ == "__main__":
    seed_cheques()