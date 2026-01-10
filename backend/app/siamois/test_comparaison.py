import os
import cv2
import numpy as np
import base64
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
import tensorflow.keras.backend as K

# --- Imports Locaux ---
from app.siamois.train import triplet_loss
from app.siamois.model import normalize_embedding

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "siamois", "siamese_best_model.h5")
DATA_SIGN_DIR = os.path.join(BASE_DIR, "data", "sign_data")
CSV_MAPPING_PATH = os.path.join(BASE_DIR, "data", "sign.xlsx - Feuil1.csv")

IMG_HEIGHT = 100
IMG_WIDTH = 200
SEUIL_DE_DECISION = 0.5

# Variable globale pour stocker le "Cœur" du modèle (Base CNN)
BASE_CNN_MODEL = None

# --- Fonctions Utilitaires ---

def normalize_embedding_tf(z):
    return K.l2_normalize(z, axis=1)

def preprocess_image_from_array(img_array):
    """Prépare une image (resize, grayscale, normalisation)"""
    try:
        if img_array is None: return None
        # Convertir en niveaux de gris si nécessaire
        if len(img_array.shape) == 3:
            img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            img = img_array
            
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        img = img.astype("float32") / 255.0
        
        # On n'ajoute qu'une seule dimension batch : (1, 100, 200, 1)
        # Contrairement à l'autre méthode, on ne duplique PAS ici.
        img = np.expand_dims(img, axis=-1)
        img = np.expand_dims(img, axis=0)
        return img
    except Exception as e:
        print(f"Erreur preprocess: {e}")
        return None

def load_siamese_model():
    """
    Charge le modèle complet et extrait le sous-modèle 'Base_CNN'.
    C'est la méthode PROPRE utilisée dans test_comparaison.py
    """
    global BASE_CNN_MODEL
    if BASE_CNN_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ ERREUR : Modèle introuvable à {MODEL_PATH}")
            return None
        try:
            print("⏳ Chargement du modèle Siamois complet...")
            # 1. Chargement du gros modèle (safe_mode=False pour Lambda layers)
            full_model = load_model(
                MODEL_PATH,
                custom_objects={'triplet_loss': triplet_loss, 'normalize_embedding': normalize_embedding_tf},
                safe_mode=False,
                compile=False
            )
            
            # 2. EXTRACTION DU CŒUR (Base_CNN)
            # Exactement comme dans votre fichier de test :
            # embedding_model = tf.keras.Model(inputs=..., outputs=...)
            BASE_CNN_MODEL = tf.keras.Model(
                inputs=full_model.get_layer('Base_CNN').input,
                outputs=full_model.get_layer('Base_CNN').output
            )
            print("✅ Cœur du modèle (Base_CNN) extrait avec succès.")

            # 3. Warm-up (Préchauffage)
            print("🔥 Préchauffage du modèle optimisé...")
            dummy = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, 1), dtype=np.float32)
            # Ici, on ne passe qu'UNE SEULE image, pas 3 !
            BASE_CNN_MODEL.predict(dummy, verbose=0)
            
            print("✅ Modèle prêt et chaud (Optimisé).")
        except Exception as e:
            print(f"❌ Impossible de charger le modèle : {e}")
            return None
    return BASE_CNN_MODEL

def get_reference_signature_path(account_number: str):
    folder_id = None
    # 1. Recherche via CSV (Placeholder)
    if os.path.exists(CSV_MAPPING_PATH):
        try:
            # df = pd.read_csv(CSV_MAPPING_PATH)
            pass
        except Exception:
            pass

    # 2. Fallback : 3 derniers chiffres
    if not folder_id and len(str(account_number)) >= 3:
        folder_id = str(int(account_number[-3:])).zfill(3)

    if not folder_id: return None

    folder_path = os.path.join(DATA_SIGN_DIR, folder_id)
    if not os.path.exists(folder_path):
        return None

    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    return os.path.join(folder_path, files[0]) if files else None

def verify_signature(account_number: str, base64_signature: str):
    """
    Compare :
    1. Signature Référence (Disque Local)
    2. Signature Chèque (Reçue en Base64 depuis le frontend)
    """
    model = load_siamese_model()
    if not model:
        return False, 0.0, "Erreur chargement modèle"

    # --- A. PRÉPARATION SIGNATURE DU CHÈQUE (Transmise) ---
    try:
        if "," in base64_signature:
            base64_signature = base64_signature.split(",")[1]
        img_data = base64.b64decode(base64_signature)
        np_arr = np.frombuffer(img_data, np.uint8)
        img_question_raw = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return False, 0.0, f"Image invalide: {e}"

    # --- B. PRÉPARATION SIGNATURE DE RÉFÉRENCE (Locale) ---
    ref_path = get_reference_signature_path(account_number)
    if not ref_path:
        return False, 1.0, "Pas de signature de référence"

    img_ref_raw = cv2.imread(ref_path)
    if img_ref_raw is None:
        return False, 1.0, "Erreur lecture référence"

    # --- C. PRÉTRAITEMENT ---
    img_Q = preprocess_image_from_array(img_question_raw) # Question (Chèque)
    img_A = preprocess_image_from_array(img_ref_raw)      # Anchor (Référence)

    if img_Q is None or img_A is None:
        return False, 0.0, "Erreur prétraitement"

    # --- D. PRÉDICTION (1 par 1) ---
    # On utilise le modèle extrait, donc on passe 1 image à la fois.
    # C'est ici qu'on évite la duplication inutile.
    emb_Q = model.predict(img_Q, verbose=0)
    emb_A = model.predict(img_A, verbose=0)

    # --- E. CALCUL DISTANCE ---
    distance = np.sum(np.square(emb_Q - emb_A))
    is_valid = distance < SEUIL_DE_DECISION

    icon = "✅" if is_valid else "❌"
    print(f"🔍 Vérif Signature [Compte {account_number}] : Dist={distance:.4f} {icon}")

    return is_valid, float(distance), "Succès"