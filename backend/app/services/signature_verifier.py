import os
import cv2
import numpy as np
import base64
import time
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K

# ============================================================
# IMPORTS LOCAUX (Architecture du modèle)
# ============================================================
from app.siamois.model import create_base_cnn, create_siamese_model, IMG_HEIGHT, IMG_WIDTH, CHANNELS

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chemin vers le modèle entraîné
MODEL_PATH = os.path.join(BASE_DIR, "siamois", "siamese_best_model.h5")

# Dossier des signatures de référence
DATA_SIGN_DIR = os.path.join(BASE_DIR, "data", "sign_data")

# --- NOUVEAU : On utilise le fichier de mapping Client -> Signature ---
# Assurez-vous que ce fichier est bien présent dans backend/app/data/
CSV_MAPPING_PATH = os.path.join(BASE_DIR, "data", "clients_training_map.csv")

SEUIL_DE_DECISION = 1.0  # Ajustez selon vos tests
EMBEDDING_MODEL = None

# ============================================================
# 1. FONCTIONS UTILITAIRES
# ============================================================

def preprocess_image_from_array(img_array):
    try:
        if img_array is None:
            return None
        
        # 1. Conversion en niveaux de gris
        if len(img_array.shape) == 3:
            img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            img = img_array
            
        # 2. Amélioration du contraste (CLAHE) au lieu d'Otsu
        # Cela uniformise l'éclairage sans détruire la forme de la signature
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img = clahe.apply(img)
        img = cv2.bitwise_not(img) # Inverse les couleurs
        # 3. Redimensionnement (100x200)
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        
        # 4. Normalisation standard (Z-score ou 0-1)
        img = img.astype("float32") / 255.0
        
        # 5. Ajout des dimensions
        img = np.expand_dims(img, axis=-1)
        img = np.expand_dims(img, axis=0)
        
        return img
    except Exception as e:
        print(f"❌ Erreur preprocess: {e}")
        return None

# ============================================================
# 2. CHARGEMENT ROBUSTE DU MODÈLE
# ============================================================

def load_siamese_model():
    """Charge l'architecture et les poids pour éviter les erreurs de version."""
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ ERREUR : Modèle introuvable à {MODEL_PATH}")
            return None
        try:
            print("⏳ Construction du modèle Siamois (Architecture)...")
            input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)
            base_cnn = create_base_cnn(input_shape)
            full_model = create_siamese_model(base_cnn)
            
            print(f"⚖️ Chargement des poids depuis {os.path.basename(MODEL_PATH)}...")
            try:
                full_model.load_weights(MODEL_PATH)
            except Exception:
                full_model.load_weights(MODEL_PATH, by_name=True)

            EMBEDDING_MODEL = base_cnn
            
            # Warm-up
            print("🔥 Préchauffage du modèle...")
            dummy = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, CHANNELS), dtype=np.float32)
            EMBEDDING_MODEL.predict(dummy, verbose=0)
            print("✅ Modèle Signature prêt !")
        except Exception as e:
            print(f"❌ CRASH chargement modèle : {e}")
            return None
    return EMBEDDING_MODEL

# ============================================================
# 3. RÉCUPÉRATION INTELLIGENTE (VIA CSV)
# ============================================================

def get_reference_signature_path(account_number: str):
    """
    Cherche le dossier de signature en utilisant le fichier clients_training_map.csv
    """
    try:
        folder_id = None
        
        # 1. Nettoyage du numéro de compte (enlever les espaces)
        acc_clean = str(account_number).replace(" ", "").strip()
        
        # 2. Recherche dans le CSV
        if os.path.exists(CSV_MAPPING_PATH):
            try:
                # Lecture du CSV (délimiteur virgule souvent standard)
                df = pd.read_csv(CSV_MAPPING_PATH)
                
                # On s'assure que la colonne RIB est en string
                df['RIB'] = df['RIB'].astype(str)
                
                # LOGIQUE : On cherche si le compte (16 chiffres) est DANS le RIB (24 chiffres)
                # Le RIB = CodeBanque(3) + CodeVille(3) + Compte(16) + Clé(2)
                # Donc acc_clean doit être une sous-chaine du RIB
                
                match = df[df['RIB'].str.contains(acc_clean, na=False)]
                
                if not match.empty:
                    # On a trouvé le client !
                    # On récupère l'ID de référence (ex: 001)
                    ref_id_raw = match.iloc[0]['SIGNATURE_ID_REF']
                    
                    # On s'assure que c'est bien formaté "001" (3 chiffres)
                    folder_id = str(ref_id_raw).zfill(3)
                    print(f"✅ Client identifié via CSV ! Compte {acc_clean} -> Dossier {folder_id}")
                else:
                    print(f"⚠️ Compte {acc_clean} introuvable dans le CSV {os.path.basename(CSV_MAPPING_PATH)}")

            except Exception as e:
                print(f"⚠️ Erreur lecture CSV : {e}")

        # 3. Fallback (Secours si CSV échoue) : On garde l'ancienne logique au cas où
        if not folder_id:
            if len(acc_clean) >= 3:
                folder_id = str(int(acc_clean[-3:])).zfill(3)
                print(f"ℹ️ Fallback : Utilisation des 3 derniers chiffres -> {folder_id}")
            else:
                return None

        # 4. Construction du chemin final
        folder_path = os.path.join(DATA_SIGN_DIR, folder_id)
        
        # Gestion dossier inexistant
        if not os.path.exists(folder_path):
            print(f"❌ Dossier physique introuvable : {folder_path}")
            # Pour éviter le crash en démo, on prend le premier dossier dispo (OPTIONNEL)
            all_folders = sorted([d for d in os.listdir(DATA_SIGN_DIR) if os.path.isdir(os.path.join(DATA_SIGN_DIR, d))])
            if all_folders:
                print(f"🔄 Redirection vers dossier par défaut : {all_folders[0]}")
                folder_path = os.path.join(DATA_SIGN_DIR, all_folders[0])
            else:
                return None

        # 5. Prendre la première image
        files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        if not files:
            return None
            
        return os.path.join(folder_path, files[0])

    except Exception as e:
        print(f"❌ Erreur recherche référence: {e}")
        return None

# ============================================================
# 4. VÉRIFICATION
# ============================================================

def verify_signature(account_number: str, base64_signature: str):
    model = load_siamese_model()
    if not model:
        return False, 0.0, "Modèle IA non chargé"

    t0 = time.time()

    try:
        if "," in base64_signature:
            base64_signature = base64_signature.split(",")[1]
        img_data = base64.b64decode(base64_signature)
        np_arr = np.frombuffer(img_data, np.uint8)
        img_question_raw = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return False, 0.0, f"Image invalide: {e}"

    ref_path = get_reference_signature_path(account_number)
    if not ref_path:
        return False, 1.0, f"Ref introuvable pour {account_number}"
    
    print(f"📂 Comparaison avec référence : {os.path.basename(ref_path)}")
    
    img_ref_raw = cv2.imread(ref_path)
    if img_ref_raw is None:
        return False, 1.0, "Erreur lecture fichier réf"

    img_Q = preprocess_image_from_array(img_question_raw)
    img_A = preprocess_image_from_array(img_ref_raw)

    if img_Q is None or img_A is None:
        return False, 0.0, "Erreur prétraitement"

    emb_Q = model.predict(img_Q, verbose=0)
    emb_A = model.predict(img_A, verbose=0)

    distance = np.sum(np.square(emb_Q - emb_A))
    is_valid = distance < SEUIL_DE_DECISION
    
    t_end = time.time()
    icon = "✅" if is_valid else "🚨"
    print(f"🔍 [IA] Compte: {account_number} | Dist: {distance:.4f} | {t_end - t0:.3f}s {icon}")

    return is_valid, float(distance), "Vérification effectuée"