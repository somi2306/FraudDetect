# backend/app/services/cheque_reader.py

import cv2
import numpy as np
import os
import easyocr
from ultralytics import YOLO
import json
from ocr_corrector import OCRCorrector

# ====================================================================
# CONFIGURATION
# ====================================================================

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

# Initialisation des modèles
try:
    print("Chargement du modèle YOLO...")
    print(f"Chemin du modèle: {YOLO_WEIGHTS_PATH}")
    
    if not os.path.exists(YOLO_WEIGHTS_PATH):
        print(f"ERREUR: Le fichier modèle n'existe pas à: {YOLO_WEIGHTS_PATH}")
    
    DETECTION_MODEL = YOLO(YOLO_WEIGHTS_PATH)
    print("✅ Modèle YOLO chargé avec succès!")
    
    print("Chargement du lecteur EasyOCR (fr/en)...")
    OCR_READER = easyocr.Reader(['fr', 'en'], gpu=False)
    print("✅ EasyOCR chargé avec succès!")
    
    # Initialiser le correcteur OCR
    print("Initialisation du correcteur OCR...")
    OCR_CORRECTOR = OCRCorrector()
    print("✅ Correcteur OCR initialisé!")
    
except Exception as e:
    print(f"❌ Erreur lors du chargement des modèles: {e}")
    DETECTION_MODEL = None
    OCR_READER = None
    OCR_CORRECTOR = None

# ====================================================================
# FONCTIONS OCR/HWR
# ====================================================================

def run_ocr_on_zone(cropped_zone: np.ndarray, field_name: str, detail: int = 0) -> str:
    """Applique EasyOCR à une zone recadrée avec prétraitement"""
    if OCR_READER is None or OCR_CORRECTOR is None:
        return "OCR_ERROR"
        
    try:
        # NOUVEAU : Prétraiter l'image pour améliorer la lecture
        preprocessed = OCR_CORRECTOR.preprocess_image(cropped_zone)
        
        # Convertir en RGB pour EasyOCR
        if len(preprocessed.shape) == 2:
            rgb_zone = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2RGB)
        else:
            rgb_zone = preprocessed
            
        results = OCR_READER.readtext(rgb_zone, detail=detail, paragraph=True)
        
        if results:
            raw_text = " ".join(results).strip()
            
            # NOUVEAU : Appliquer la correction spécifique au champ
            corrected_text = OCR_CORRECTOR.correct_field(field_name, raw_text, cropped_zone)
            
            return corrected_text
        return ""
    except Exception as e:
        print(f"Erreur OCR pour {field_name}: {e}")
        return f"OCR_FAIL: {e}"

# ====================================================================
# FONCTION PRINCIPALE D'EXTRACTION
# ====================================================================

def detect_and_read_cheque_zones(image_path: str) -> dict:
    """Détecte, recadre et lit les zones d'un chèque avec correction OCR"""
    if DETECTION_MODEL is None or OCR_READER is None or OCR_CORRECTOR is None:
        return {"status": "ERROR", "message": "Les modèles ML ne sont pas chargés."}

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

    # PARCOURIR LES RÉSULTATS DE DÉTECTION
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = LABELS[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            
            detection_count += 1
            print(f"Détection: {label} - confiance: {confidence:.2f}")
            
            # Application d'un padding
            padding = 10 
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(W, x2 + padding)
            y2 = min(H, y2 + padding)

            # RECADRAGE DE LA ZONE
            cropped_zone = img[y1:y2, x1:x2]
            
            if cropped_zone.size == 0:
                print(f"Zone vide pour {label}")
                continue
            
            # RECONNAISSANCE AVEC CORRECTION
            if label == "Signature":
                extracted_data[label] = {
                    "confidence": f"{confidence:.2f}",
                    "bounding_box": (x1, y1, x2, y2),
                    "status": "Image Capturée pour Vérification"
                }
            else:
                # NOUVEAU : Passer le nom du champ pour correction ciblée
                text = run_ocr_on_zone(cropped_zone, label)
                
                extracted_data[label] = {
                    "text": text, 
                    "confidence": f"{confidence:.2f}",
                    "bounding_box": (x1, y1, x2, y2)
                }

    print(f"Total des détections: {detection_count}")
    
    # NOUVEAU : Validation des données extraites
    if extracted_data and OCR_CORRECTOR:
        validation_issues = OCR_CORRECTOR.validate_extraction(extracted_data)
        if validation_issues:
            print("\n⚠️  Avertissements de validation:")
            for field, issue in validation_issues.items():
                print(f"   - {field}: {issue}")
    
    if not extracted_data:
        return {"status": "SUCCESS", "message": "Aucune zone détectée sur le chèque."}
        
    return {"status": "SUCCESS", "data": extracted_data}

# ====================================================================
# UTILISATION
# ====================================================================
if __name__ == "__main__":
    TEST_IMAGE_PATH = "/Users/mac/Documents/FraudDetect/backend/public/cheque_ID401_BEN896_M7601.07.png"
    
    print(f"Tentative de lecture de: {TEST_IMAGE_PATH}")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"ERREUR: Le fichier image est introuvable à {TEST_IMAGE_PATH}")
        public_dir = os.path.dirname(TEST_IMAGE_PATH)
        if os.path.exists(public_dir):
            for item in os.listdir(public_dir):
                print(f"  - {item}")
    else:
        print("\n" + "="*70)
        print("TRAITEMENT AVEC CORRECTION OCR")
        print("="*70 + "\n")
        
        results = detect_and_read_cheque_zones(TEST_IMAGE_PATH)
        
        print("\n" + "="*70)
        print("RÉSULTATS D'EXTRACTION CORRIGÉS")
        print("="*70)
        print(json.dumps(results, indent=4, ensure_ascii=False))