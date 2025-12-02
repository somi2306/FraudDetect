# backend/app/services/cheque_reader.py

import cv2
import numpy as np
import os
import easyocr
from ultralytics import YOLO
import json

# ====================================================================
# CONFIGURATION
# ====================================================================

# CORRECTION DU CHEMIN : votre modèle est dans cheque_detection_cih11, pas cheque_detection_cih
YOLO_WEIGHTS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "runs", "cheque_detection_combined13", "weights", "best.pt"
))

# Les labels dans l'ordre de votre fichier obj.names (9 classes)
LABELS = [
    "Signature", "Montant_Chiffres", "Montant_Lettres", 
    "Beneficiaire", "Date", "Lieu", 
    "Ligne_MICR", "Num_Cheque", "Num_Compte"
]

# Initialisation des modèles (à faire une seule fois au démarrage de l'application)
try:
    print("Chargement du modèle YOLO...")
    print(f"Chemin du modèle: {YOLO_WEIGHTS_PATH}")
    
    # Vérifier si le fichier existe
    if not os.path.exists(YOLO_WEIGHTS_PATH):
        print(f"ERREUR: Le fichier modèle n'existe pas à: {YOLO_WEIGHTS_PATH}")
        # Lister les fichiers disponibles pour debug
        runs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "runs"))
        if os.path.exists(runs_dir):
            print("Contenu du dossier 'runs':")
            for item in os.listdir(runs_dir):
                print(f"  - {item}")
    
    DETECTION_MODEL = YOLO(YOLO_WEIGHTS_PATH)
    print("✅ Modèle YOLO chargé avec succès!")
    
    # Charger EasyOCR. Utiliser 'fr' et 'en' pour le français et l'anglais.
    print("Chargement du lecteur EasyOCR (fr/en)...")
    OCR_READER = easyocr.Reader(['fr', 'en'], gpu=False) # Mettez gpu=True si vous avez un GPU
    print("✅ EasyOCR chargé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur lors du chargement des modèles: {e}")
    DETECTION_MODEL = None
    OCR_READER = None

# ====================================================================
# FONCTIONS OCR/HWR
# ====================================================================

def run_ocr_on_zone(cropped_zone: np.ndarray, detail: int = 0) -> str:
    """Applique EasyOCR à une zone recadrée."""
    if OCR_READER is None:
        return "OCR_ERROR"
        
    try:
        # Convertir en RGB si nécessaire
        if len(cropped_zone.shape) == 3 and cropped_zone.shape[2] == 3:
            rgb_zone = cv2.cvtColor(cropped_zone, cv2.COLOR_BGR2RGB)
        else:
            rgb_zone = cropped_zone
            
        results = OCR_READER.readtext(rgb_zone, detail=detail, paragraph=True)
        if results:
            # detail=0 retourne une liste de chaînes de caractères lues
            return " ".join(results).strip()
        return ""
    except Exception as e:
        print(f"Erreur OCR: {e}")
        return f"OCR_FAIL: {e}"

# ====================================================================
# FONCTION PRINCIPALE D'EXTRACTION
# ====================================================================

def detect_and_read_cheque_zones(image_path: str) -> dict:
    """Détecte, recadre et lit les zones d'un chèque."""
    if DETECTION_MODEL is None or OCR_READER is None:
        return {"status": "ERROR", "message": "Les modèles ML ne sont pas chargés."}

    # Vérifier si l'image existe
    if not os.path.exists(image_path):
        return {"status": "ERROR", "message": f"Image introuvable: {image_path}"}

    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "message": f"Impossible de charger l'image: {image_path}"}

    H, W, _ = img.shape
    print(f"Image chargée: {W}x{H} pixels")
    
    results = DETECTION_MODEL(img, verbose=False)
    
    extracted_data = {}
    detection_count = 0

    # 1. PARCOURIR LES RÉSULTATS DE DÉTECTION
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = LABELS[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            
            detection_count += 1
            print(f"Détection: {label} - confiance: {confidence:.2f}")
            
            # Application d'un padding léger (important pour le HWR/OCR)
            padding = 10 
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(W, x2 + padding)
            y2 = min(H, y2 + padding)

            # 2. RECADRAGE DE LA ZONE
            cropped_zone = img[y1:y2, x1:x2]
            
            # Vérifier que la zone recadrée n'est pas vide
            if cropped_zone.size == 0:
                print(f"Zone vide pour {label}")
                continue
            
            # --- 3. RECONNAISSANCE (OCR/HWR) ---
            
            if label == "Signature":
                # Pour la signature, nous ne faisons pas d'OCR, nous la sauvegardons.
                extracted_data[label] = {
                    "confidence": f"{confidence:.2f}",
                    "bounding_box": (x1, y1, x2, y2),
                    "status": "Image Capturée pour Vérification"
                }
            else:
                # Appliquer l'OCR pour les autres champs
                text = run_ocr_on_zone(cropped_zone)
                
                extracted_data[label] = {
                    "text": text, 
                    "confidence": f"{confidence:.2f}",
                    "bounding_box": (x1, y1, x2, y2)
                }

    print(f"Total des détections: {detection_count}")
    
    if not extracted_data:
        return {"status": "SUCCESS", "message": "Aucune zone détectée sur le chèque."}
        
    return {"status": "SUCCESS", "data": extracted_data}

# ====================================================================
# UTILISATION
# ====================================================================
if __name__ == "__main__":
    # Chemin vers l'image de test
    TEST_IMAGE_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        "..", "..", "..", "backend", "public", "cheque_trans_39.png"
    ))
    
    print(f"Tentative de lecture de: {TEST_IMAGE_PATH}")
    
    # Vérification que le fichier existe avant de lancer le traitement lourd
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"ERREUR: Le fichier image est introuvable à {TEST_IMAGE_PATH}")
        print("Fichiers disponibles dans backend/public/:")
        public_dir = os.path.dirname(TEST_IMAGE_PATH)
        if os.path.exists(public_dir):
            for item in os.listdir(public_dir):
                print(f"  - {item}")
    else:
        results = detect_and_read_cheque_zones(TEST_IMAGE_PATH)
        
        print("\n--- RÉSULTATS D'EXTRACTION ---")
        # Utilisation de ensure_ascii=False pour afficher correctement les caractères français
        print(json.dumps(results, indent=4, ensure_ascii=False)) 