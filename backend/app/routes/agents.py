from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import tempfile
import shutil
import requests
from datetime import datetime

# --- Imports Internes ---
from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
from ..models.cheque import Cheque
from ..models.details_cheque import DetailsCheque
from ..utils.auth import get_current_user

# --- Services ---
from ..services.websocket_manager import manager
from ..services.cheque_reader import detect_and_read_cheque_zones
from ..services.signature_verifier import verify_signature # <--- IMPORT

router = APIRouter(
    tags=["Agents Management"]
)

# -----------------------------------------------------------------------------
# 1. CONFIRMATION RESET PASSWORD
# -----------------------------------------------------------------------------
@router.put("/confirm-reset")
def confirm_password_reset(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé.")
    agent.must_reset_password = False
    db.commit()
    return {"status": "success"}

# -----------------------------------------------------------------------------
# 2. RÉCUPÉRATION DES CHÈQUES ASSIGNÉS (DASHBOARD)
# -----------------------------------------------------------------------------
@router.get("/cheques/me")
def get_my_cheques(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("user_id")

    # Trouver l'agent
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    if not agent.bank_id:
        raise HTTPException(status_code=400, detail="Aucune banque associée à cet agent.")

    # Requête de base
    beneficiaire_condition = (
        db.query(Cheque, User)
        .join(User, Cheque.beneficiaire_id == User.id)
        .filter(
            User.bank_id == agent.bank_id,
            Cheque.status.in_(["pending", "uploaded"])
        )
    )

    # A. Chèques INTERNES
    cheques_meme_banque_raw = beneficiaire_condition.filter(
        Cheque.banque_cible_id == agent.bank_id
    ).all()

    cheques_meme_banque = [
        {
            "cheque": {
                **cheque.__dict__,
                "imageUrl": f"/public/{cheque.image_url}" if not cheque.image_url.startswith("http") else cheque.image_url
            },
            "beneficiaire": {
                "id": beneficiaire.id,
                "name": f"{beneficiaire.first_name} {beneficiaire.last_name}",
                "email": beneficiaire.email
            }
        }
        for cheque, beneficiaire in cheques_meme_banque_raw
    ]

    # B. Chèques EXTERNES
    cheques_autre_banque_raw = beneficiaire_condition.filter(
        Cheque.banque_cible_id != agent.bank_id
    ).all()

    cheques_autre_banque = [
        {
            "cheque": {
                **cheque.__dict__,
                "imageUrl": f"/public/{cheque.image_url}" if not cheque.image_url.startswith("http") else cheque.image_url
            },
            "beneficiaire": {
                "id": beneficiaire.id,
                "name": f"{beneficiaire.first_name} {beneficiaire.last_name}",
                "email": beneficiaire.email
            }
        }
        for cheque, beneficiaire in cheques_autre_banque_raw
    ]

    return {
        "agentName": f"{agent.first_name} {agent.last_name}",
        "agentEmail": agent.email,
        "agentBankId": agent.bank_id,
        "cheques_meme_banque": cheques_meme_banque,
        "cheques_autre_banque": cheques_autre_banque,
    }

# -----------------------------------------------------------------------------
# 3. ANALYSE IA DU CHÈQUE (OCR / YOLO)
# -----------------------------------------------------------------------------
@router.post("/cheque/analyze/{cheque_id}")
async def analyze_cheque(
    cheque_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Récupérer le chèque
    cheque = db.query(Cheque).filter(Cheque.id == cheque_id).first()
    if not cheque:
        raise HTTPException(404, "Chèque introuvable.")

    image_source = cheque.image_url
    tmp_path = None
    
    try:
        # 2. Préparer l'image locale pour OpenCV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = tmp.name

        if image_source.startswith("http"):
            response = requests.get(image_source, stream=True)
            if response.status_code == 200:
                with open(tmp_path, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
            else:
                raise HTTPException(400, "Impossible de télécharger l'image source.")
        else:
            base_dir = os.getcwd()
            possible_path_public = os.path.join(base_dir, "public", image_source)
            possible_path_direct = os.path.abspath(image_source)

            if os.path.exists(possible_path_public):
                shutil.copy(possible_path_public, tmp_path)
            elif os.path.exists(possible_path_direct):
                shutil.copy(possible_path_direct, tmp_path)
            elif os.path.exists(os.path.join(base_dir, image_source)): 
                 shutil.copy(os.path.join(base_dir, image_source), tmp_path)
            else:
                raise HTTPException(404, f"Fichier image local introuvable : {image_source}")

        # 3. Appel du service d'analyse
        print(f"🖼️ Analyse de l'image temporaire : {tmp_path}")
        results = detect_and_read_cheque_zones(tmp_path)
        
        return results

    except Exception as e:
        print(f"❌ Erreur analyse : {e}")
        raise HTTPException(500, detail=f"Erreur lors de l'analyse : {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer le fichier temp {tmp_path}: {e}")

# -----------------------------------------------------------------------------
# 4. VALIDATION ET SAUVEGARDE DES DÉTAILS
# -----------------------------------------------------------------------------
@router.post("/cheque/validate/{cheque_id}")
async def validate_cheque(
    cheque_id: int,
    data: dict = Body(...), # Les données corrigées (OCR + Agent)
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Valide le chèque :
    1. Récupère les données corrigées par l'agent.
    2. Vérifie la signature via le modèle Siamois (IA).
    3. Enregistre les détails et met à jour le statut (Approved ou rejected).
    """
    
    # 1. Vérification Agent
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(User.clerk_id == clerk_id, User.role == UserRole.AGENT).first()
    
    if not agent:
        raise HTTPException(404, "Agent non autorisé.")

    cheque = db.query(Cheque).filter(Cheque.id == cheque_id).first()
    if not cheque:
        raise HTTPException(404, "Chèque introuvable.")

    try:
        # Fonction utilitaire pour extraire la valeur texte en toute sécurité
        def get_val(key):
            return data.get(key, {}).get("text", "")

        # ---------------------------------------------------------
        # 2. PRÉPARATION DES DONNÉES
        # ---------------------------------------------------------

        # A. Traitement de la Date (Parsing robuste)
        raw_date = get_val("Date")
        date_obj = datetime.now().date() # Par défaut : aujourd'hui
        try:
            if raw_date:
                # Nettoyage : 29.11.2025 -> 29/11/2025
                clean_date = raw_date.replace('.', '/').replace('-', '/').replace(' ', '')
                date_obj = datetime.strptime(clean_date, "%d/%m/%Y").date()
        except ValueError:
            print(f"⚠️ Format de date invalide '{raw_date}', utilisation date du jour.")

        # B. Récupération Signature & Compte pour vérification
        signature_b64 = data.get("Signature", {}).get("base64_image", "")
        # On utilise le numéro de compte corrigé par l'agent pour trouver la bonne référence
        num_compte_corrigé = get_val("Num_Compte")
        # Appel au Siamois
        if signature_b64 and num_compte_corrigé:
            is_valid, distance, msg = verify_signature(num_compte_corrigé, signature_b64)
        # ---------------------------------------------------------
        # 3. VÉRIFICATION DE LA SIGNATURE (SIAMOIS)
        # ---------------------------------------------------------
        
        signature_status = "Non vérifiée"
        fraud_score = 0.0 # Distance (plus c'est grand, moins ça ressemble)
        message_retour = "Chèque validé avec succès."
        new_status = "approved"

        if signature_b64 and num_compte_corrigé:
            print(f"🤖 Lancement vérification signature pour le compte {num_compte_corrigé}...")
            
            # Appel au service IA
            is_valid, distance, msg = verify_signature(num_compte_corrigé, signature_b64)
            
            fraud_score = distance
            
            if is_valid:
                signature_status = "Authentique"
                new_status = "approved"
                message_retour = f"✅ Signature validée (Distance: {distance:.4f})"
            else:
                signature_status = "Suspecte"
                new_status = "rejected" # On alerte sans bloquer définitivement, ou "rejected"
                message_retour = f"⚠️ ALERTE FRAUDE : Signature suspecte (Distance: {distance:.4f})"
                print(f"🚨 ALERTE : Signature divergente pour le chèque {cheque_id}")
        else:
            print("⚠️ Pas de signature ou de numéro de compte pour vérification.")

        # ---------------------------------------------------------
        # 4. SAUVEGARDE EN BASE DE DONNÉES
        # ---------------------------------------------------------

        # Vérifier si un détail existe déjà (Update vs Create)
        existing_detail = db.query(DetailsCheque).filter(DetailsCheque.cheque_id == cheque.id).first()

        if existing_detail:
            # Update
            existing_detail.numero_cheque = get_val("Num_Cheque")
            existing_detail.montant_chiffre = get_val("Montant_Chiffres")
            existing_detail.montant_lettre = get_val("Montant_Lettres")
            existing_detail.date_emission = date_obj
            existing_detail.lieu = get_val("Lieu")
            existing_detail.numero_compte = num_compte_corrigé
            existing_detail.beneficiaire = get_val("Beneficiaire")
            existing_detail.signature = signature_b64
        else:
            # Create
            new_detail = DetailsCheque(
                cheque_id=cheque.id,
                numero_cheque=get_val("Num_Cheque"),
                montant_chiffre=get_val("Montant_Chiffres"),
                montant_lettre=get_val("Montant_Lettres"),
                date_emission=date_obj,
                lieu=get_val("Lieu"),
                numero_compte=num_compte_corrigé,
                beneficiaire=get_val("Beneficiaire"),
                signature=signature_b64
            )
            db.add(new_detail)

        # Mise à jour du statut global du chèque
        cheque.status = new_status
        
        db.commit()

        return {
            "status": "success", 
            "message": message_retour, 
            "cheque_status": new_status,
            "fraud_score": fraud_score
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur validation chèque: {e}")
        raise HTTPException(500, detail=f"Erreur lors de la sauvegarde : {str(e)}")
    
# -----------------------------------------------------------------------------
# 5. TRANSMISSION INTERBANCAIRE
# -----------------------------------------------------------------------------
@router.post("/cheque/transmettre/{cheque_id}")
async def transmettre_cheque(
    cheque_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(404, "Agent non trouvé.")

    cheque = db.query(Cheque).filter(Cheque.id == cheque_id).first()

    if not cheque:
        raise HTTPException(404, "Chèque introuvable.")

    if cheque.banque_cible_id == agent.bank_id:
        raise HTTPException(
            400, "Ce chèque doit être traité ici (interne), pas transmis.")

    agent_cible = db.query(User).filter(
        User.bank_id == cheque.banque_cible_id,
        User.role == UserRole.AGENT,
        User.is_active == True 
    ).first()

    if not agent_cible:
        raise HTTPException(404, "Aucun agent disponible trouvé pour la banque cible.")

    cheque.status = "transmitted"
    cheque.agent_actuel_id = agent_cible.id

    db.commit()

    # Notification WebSocket
    try:
        if agent_cible.clerk_id:
            await manager.send_personal_message(
                {
                    "type": "CHEQUE_RECEIVED",
                    "title": "Nouveau chèque reçu",
                    "message": f"Le chèque #{cheque.id} vous a été transmis pour traitement.",
                    "cheque_id": cheque.id
                },
                agent_cible.clerk_id
            )
    except Exception as e:
        print(f"⚠️ Erreur notification WS: {e}")

    return {"message": "Chèque transmis avec succès"}

# -----------------------------------------------------------------------------
# 6. HISTORIQUE DES TRANSMISSIONS
# -----------------------------------------------------------------------------
@router.get("/cheques/transmis")
def get_cheques_transmis(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(404, "Agent introuvable")

    cheques = (
        db.query(Cheque)
        .join(User, Cheque.beneficiaire_id == User.id)
        .join(Bank, User.bank_id == Bank.id)
        .options(joinedload(Cheque.beneficiaire))
        .filter(
            Cheque.agent_actuel_id == agent.id,
            Cheque.status == "transmitted"
        )
        .all()
    )

    result = []
    for ch in cheques:
        result.append({
            "cheque": {
                "id": ch.id,
                "imageUrl": f"/public/{ch.image_url}" if not ch.image_url.startswith("http") else ch.image_url,
                "status": ch.status
            },
            "beneficiaire": {
                "id": ch.beneficiaire.id,
                "name": f"{ch.beneficiaire.first_name} {ch.beneficiaire.last_name}",
                "bankName": ch.beneficiaire.bank.name if ch.beneficiaire.bank else "Inconnue"
            }
        })
    return result

# -----------------------------------------------------------------------------
# 7. INFO AGENT COURANT
# -----------------------------------------------------------------------------
@router.get("/me")
def get_my_agent(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    if clerk_id is None:
        raise HTTPException(status_code=401, detail="Non authentifié")

    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")

    return {
        "id": agent.id,
        "name": f"{agent.last_name} {agent.first_name}",
        "email": agent.email,
        "bankId": agent.bank_id,
    }

# -----------------------------------------------------------------------------
# 8. CHÈQUES TRAITÉS (HISTORIQUE)
# -----------------------------------------------------------------------------
@router.get("/cheques/traites")
def get_cheques_traite(
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    cheques = (
        db.query(Cheque)
        .join(User, Cheque.beneficiaire_id == User.id)
        .options(joinedload(Cheque.beneficiaire))
        .filter(
            Cheque.agent_actuel_id == agent.id, 
            Cheque.status.in_(["rejected", "approved", "validated"])
        )
        .all()
    )

    result = []
    for ch in cheques:
        result.append({
            "cheque": {
                "id": ch.id,
                "date_depot": ch.date_depot,
                "imageUrl": f"/public/{ch.image_url}" if not ch.image_url.startswith("http") else ch.image_url,
                "status": ch.status
            },
            "beneficiaire": {
                "id": ch.beneficiaire.id,
                "name": f"{ch.beneficiaire.first_name} {ch.beneficiaire.last_name}",
                "bankName": ch.beneficiaire.bank.name if ch.beneficiaire.bank else ""
            }
        })

    return result