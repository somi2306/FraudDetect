import cv2
import numpy as np
import os
import easyocr
from ultralytics import YOLO
import json
import re
import base64
import difflib

# ====================================================================
# CONFIGURATION
# ====================================================================

# Liste pour correction villes
VILLES_MAROC = [
    "Rabat", "Casablanca", "Marrakech", "Fès", "Tanger",
    "Agadir", "Oujda", "Meknès", "Laâyoune", "Kenitra",
    "Salé", "Tétouan", "Safi", "Mohammedia", "Khouribga",
    "Béni Mellal", "El Jadida", "Taza", "Nador", "Settat",
    "Berkane", "Khemisset", "Guelmim", "Errachidia"
]

# Mapping simple pour détecter le premier chiffre via le texte
CHIFFRES_LETTRES = {
    "un": "1", "une": "1", "deux": "2", "trois": "3", "quatre": "4",
    "cinq": "5", "six": "6", "sept": "7", "huit": "8", "neuf": "9",
    "dix": "1", "onze": "1", "douze": "1", "treize": "1", "quatorze": "1",
    "quinze": "1", "seize": "1", "vingt": "2", "trente": "3", 
    "quarante": "4", "cinquante": "5", "soixante": "6",
    "cent": "1", "mille": "1" 
    # (Note: mille/cent commencent par 1, ex: "mille dirhams" = 1000)
}

YOLO_WEIGHTS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "runs", "cheque_detection_combined13", "weights", "best.pt"
))

LABELS = [
    "Signature", "Montant_Chiffres", "Montant_Lettres", 
    "Beneficiaire", "Date", "Lieu", 
    "Ligne_MICR", "Num_Cheque", "Num_Compte"
]

try:
    print("Chargement du modèle YOLO...")
    if not os.path.exists(YOLO_WEIGHTS_PATH):
        print(f"ERREUR: Le fichier modèle n'existe pas à: {YOLO_WEIGHTS_PATH}")
    
    DETECTION_MODEL = YOLO(YOLO_WEIGHTS_PATH)
    print("✅ Modèle YOLO chargé avec succès!")
    
    print("Chargement du lecteur EasyOCR (fr/en)...")
    OCR_READER = easyocr.Reader(['fr', 'en'], gpu=False) 
    print("✅ EasyOCR chargé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur lors du chargement des modèles: {e}")
    DETECTION_MODEL = None
    OCR_READER = None

# ====================================================================
# FONCTIONS INTELLIGENTES
# ====================================================================

def get_expected_start_digit(text_amount: str) -> str:
    """
    Analyse le montant en lettres pour deviner par quel chiffre le montant doit commencer.
    Ex: "Sept mille..." -> Retourne "7"
    """
    if not text_amount: return None
    
    # Nettoyage et découpage en mots
    words = re.sub(r"[^a-zA-Zàâäéèêëîïôöùûüç ]", " ", text_amount.lower()).split()
    
    for word in words:
        # Correction fuzzy légère (ex: "quanante" -> "quarante")
        match = difflib.get_close_matches(word, CHIFFRES_LETTRES.keys(), n=1, cutoff=0.8)
        if match:
            return CHIFFRES_LETTRES[match[0]]
            
    return None

def correct_digits_with_text(digits: str, text_amount: str) -> str:
    """
    Corrige le montant en chiffres (ex: 47900.43) en utilisant le texte (ex: Sept mille...).
    """
    if not digits or not text_amount: return digits
    
    expected_start = get_expected_start_digit(text_amount)
    
    # Si on n'a rien trouvé dans le texte, on ne touche à rien
    if not expected_start: return digits
    
    # Cas 1 : Le montant commence déjà bien (ex: 7900 vs 7) -> OK
    if digits.startswith(expected_start):
        return digits
        
    # Cas 2 : Le montant a un bruit au début (ex: 47900 vs 7)
    # On vérifie si le 2ème caractère correspond
    if len(digits) > 1 and digits[1] == expected_start:
        print(f"💰 Correction Montant: Suppression du bruit '{digits[0]}' au début ({digits} -> {digits[1:]})")
        return digits[1:]
        
    return digits

def correct_city_name(text: str) -> str:
    if not text or len(text) < 3: return text
    clean = re.sub(r"[^a-zA-ZàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ ]", "", text).strip()
    matches = difflib.get_close_matches(clean, VILLES_MAROC, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    return text

def clean_ocr_text(text: str, label: str) -> str:
    if not text: return ""
    text = text.strip()

    if label == "Montant_Chiffres":
        # Regex stricte pour garder le format numérique
        # On supprime tout sauf chiffres, points, virgules
        cleaned = re.sub(r"[^0-9.,]", "", text)
        # On remplace , par . pour uniformiser
        return cleaned.replace(',', '.')

    elif label in ["Num_Compte", "Num_Cheque", "Ligne_MICR"]:
        return re.sub(r"\D", "", text)

    elif label == "Lieu":
        return correct_city_name(text)
        
    elif label == "Date":
        return text

    else:
        # Montant Lettres, Beneficiaire
        return re.sub(r"[#|_=<>*]", "", text).strip()

def image_to_base64(image_array: np.ndarray) -> str:
    try:
        _, buffer = cv2.imencode('.png', image_array)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        return ""

def run_ocr_on_zone(cropped_zone: np.ndarray) -> str:
    if OCR_READER is None: return "OCR_ERROR"
    try:
        if len(cropped_zone.shape) == 3 and cropped_zone.shape[2] == 3:
            rgb_zone = cv2.cvtColor(cropped_zone, cv2.COLOR_BGR2RGB)
        else:
            rgb_zone = cropped_zone
        results = OCR_READER.readtext(rgb_zone, detail=0, paragraph=True)
        return " ".join(results).strip() if results else ""
    except Exception as e:
        return f"OCR_FAIL: {e}"

# ====================================================================
# MAIN
# ====================================================================

def detect_and_read_cheque_zones(image_path: str) -> dict:
    if DETECTION_MODEL is None or OCR_READER is None:
        return {"status": "ERROR", "message": "Les modèles ML ne sont pas chargés."}

    if not os.path.exists(image_path):
        return {"status": "ERROR", "message": f"Image introuvable: {image_path}"}

    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "message": "Impossible de charger l'image"}

    H, W, _ = img.shape
    results = DETECTION_MODEL(img, verbose=False)
    
    extracted_data = {}
    temp_results = {} # Pour stocker les labels temporaires avant post-processing

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = LABELS[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            
            if label in temp_results and temp_results[label]['confidence'] > confidence:
                continue

            # Padding
            pad = 5
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(W, x2 + pad), min(H, y2 + pad)

            cropped_zone = img[y1:y2, x1:x2]
            if cropped_zone.size == 0: continue

            data_entry = {
                "confidence": f"{confidence:.2f}",
                "bounding_box": (x1, y1, x2, y2)
            }

            if label == "Signature":
                base64_img = image_to_base64(cropped_zone)
                data_entry["base64_image"] = f"data:image/png;base64,{base64_img}"
                data_entry["text"] = "Signature Détectée"
                data_entry["is_image"] = True
            else:
                raw_text = run_ocr_on_zone(cropped_zone)
                clean_text = clean_ocr_text(raw_text, label)
                
                data_entry["text"] = clean_text
                data_entry["is_image"] = False

            extracted_data[label] = data_entry
            temp_results[label] = {'confidence': confidence}

    # --- VALIDATION CROISÉE FINALE ---
    if "Montant_Chiffres" in extracted_data and "Montant_Lettres" in extracted_data:
        amount_digits = extracted_data["Montant_Chiffres"]["text"]
        amount_text = extracted_data["Montant_Lettres"]["text"]
        
        # Correction intelligente : 47900.43 + "sept mille" -> 7900.43
        corrected_digits = correct_digits_with_text(amount_digits, amount_text)
        
        extracted_data["Montant_Chiffres"]["text"] = corrected_digits

    if not extracted_data:
        return {"status": "SUCCESS", "message": "Aucune zone détectée.", "data": {}}
        
    return {"status": "SUCCESS", "data": extracted_data}