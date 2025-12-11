# backend/app/services/ocr_corrector.py

import re
import cv2
import numpy as np
from typing import Dict, Tuple

class OCRCorrector:
    """Classe pour corriger les erreurs OCR des chèques manuscrits"""
    
    def __init__(self):
        # Dictionnaire des confusions courantes en écriture manuscrite
        self.char_corrections = {
            # Lettres confondues avec chiffres
            'O': '0', 'o': '0',
            'l': '1', 'I': '1',
            'Z': '2', 'z': '2',
            'S': '5', 's': '5',
            'G': '6', 'g': '6',
            'T': '7',
            'B': '8',
            # Caractères parasites
            "'": '', '"': '', '(': '', ')': '', 
            '«': '', '»': '', '`': '',
        }
        
        # Corrections spécifiques pour montants en lettres (français)
        self.word_corrections = {
            'MIP2C': 'MILLE',
            'MIPPC': 'MILLE',
            'MIL2C': 'MILLE',
            'MILPC': 'MILLE',
            'M1LLE': 'MILLE',
            'M1L2C': 'MILLE',
            'SePT': 'SEPT',
            'SeP7': 'SEPT',
            'S3PT': 'SEPT',
            'C3NT': 'CENT',
            'CFNT': 'CENT',
            'C£NT': 'CENT',
            'UN3': 'UNE',
            'DIRhAMS': 'DIRHAMS',
            'DIRH4MS': 'DIRHAMS',
            'C3NTIMES': 'CENTIMES',
            'CFNTIMES': 'CENTIMES',
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Améliore la qualité de l'image avant OCR"""
        # Conversion en niveaux de gris si nécessaire
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Augmentation du contraste avec CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Réduction du bruit
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def correct_beneficiaire(self, text: str) -> str:
        """Corrige le nom du bénéficiaire"""
        if not text:
            return text
        
        # Nettoyer les apostrophes et guillemets au début
        text = text.lstrip("'\"`")
        
        # Corrections courantes pour les noms
        corrections = {
            'abif': 'Nabil',
            'Fabif': 'Nabil',
            'l\'labif': 'Nabil',
            'Badasui': 'Badaoui',
            'Badaoui': 'Badaoui',
        }
        
        for wrong, right in corrections.items():
            text = re.sub(wrong, right, text, flags=re.IGNORECASE)
        
        # Capitaliser correctement (Première lettre de chaque mot en majuscule)
        text = ' '.join(word.capitalize() for word in text.split())
        
        return text.strip()
    
    def correct_montant_lettres(self, text: str) -> str:
        """Corrige le montant écrit en lettres"""
        if not text:
            return text
        
        # Convertir en majuscules pour uniformiser
        text = text.upper()
        
        # Appliquer les corrections de mots
        for wrong, right in self.word_corrections.items():
            text = re.sub(r'\b' + wrong + r'\b', right, text)
        
        # Nettoyer les caractères parasites
        text = re.sub(r'[\'\"`,_\(\)]', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Extraire uniquement la partie du montant (avant "Payez" ou texte arabe)
        match = re.search(r'((?:ZERO|UN|DEUX|TROIS|QUATRE|CINQ|SIX|SEPT|HUIT|NEUF|DIX|ONZE|DOUZE|TREIZE|QUATORZE|QUINZE|SEIZE|VINGT|TRENTE|QUARANTE|CINQUANTE|SOIXANTE|CENT|MILLE|MILLION|ET|UNE)+\s*)+DIRHAMS?\s*(?:ET\s+)?(?:\w+\s+)?CENTIMES?', text)
        
        if match:
            return match.group(0).strip()
        
        return text.strip()
    
    def correct_num_cheque(self, text: str) -> str:
        """Corrige le numéro de chèque"""
        if not text:
            return text
        
        # Supprimer les parenthèses et autres caractères parasites
        text = re.sub(r'[^\d\sN:n°-]', '', text)
        
        # Extraire uniquement les chiffres après N: ou N°
        match = re.search(r'[Nn]\s*[:°]?\s*(\d+)', text)
        if match:
            return f"N: {match.group(1)}"
        
        # Si pas de format N:, extraire juste les chiffres
        numbers = re.findall(r'\d+', text)
        if numbers:
            return f"N: {numbers[0]}"
        
        return text.strip()
    
    def correct_ligne_micr(self, text: str) -> str:
        """Corrige la ligne MICR (uniquement chiffres et symboles MICR)"""
        if not text:
            return text
        
        # Remplacer les guillemets par le séparateur MICR approprié
        text = text.replace('"', ':')
        text = text.replace("'", ':')
        text = text.replace('«', ':')
        text = text.replace('»', ':')
        
        # Garder uniquement chiffres, deux-points et espaces
        text = re.sub(r'[^\d:\s]', '', text)
        
        # Normaliser les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def correct_date(self, text: str) -> str:
        """Valide et corrige le format de date"""
        if not text:
            return text
        
        # Extraire les chiffres de la date
        date_pattern = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
        match = re.search(date_pattern, text)
        
        if match:
            day, month, year = match.groups()
            # Reformater avec zéros initiaux si nécessaire
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        return text.strip()
    
    def correct_lieu(self, text: str) -> str:
        """Corrige le lieu"""
        if not text:
            return text
        
        # Supprimer underscore et autres caractères parasites
        text = text.replace('_', '').replace('-', ' ')
        
        # Capitaliser correctement
        text = text.title()
        
        return text.strip()
    
    def correct_montant_chiffres(self, text: str) -> str:
        """Corrige le montant en chiffres"""
        if not text:
            return text
        
        # Remplacer # par rien (c'est juste un marqueur de sécurité)
        text = text.replace('#', '')
        
        # Appliquer les corrections de caractères
        for wrong, right in self.char_corrections.items():
            if wrong in ['O', 'o', 'l', 'I', 'S']:
                text = text.replace(wrong, right)
        
        # Extraire le montant au format XX.XX ou XXXX.XX
        match = re.search(r'(\d+)[\s.](\d{2})', text)
        if match:
            entier, decimal = match.groups()
            return f"{entier}.{decimal}"
        
        # Si pas de décimales trouvées, extraire juste les chiffres
        numbers = re.findall(r'\d+', text)
        if numbers:
            return '.'.join(numbers)
        
        return text.strip()
    
    def correct_field(self, field_name: str, text: str, image: np.ndarray = None) -> str:
        """Applique la correction appropriée selon le champ"""
        if not text:
            return text
        
        # Mapper chaque champ à sa fonction de correction
        corrections_map = {
            'Beneficiaire': self.correct_beneficiaire,
            'Montant_Lettres': self.correct_montant_lettres,
            'Montant_Chiffres': self.correct_montant_chiffres,
            'Num_Cheque': self.correct_num_cheque,
            'Ligne_MICR': self.correct_ligne_micr,
            'Date': self.correct_date,
            'Lieu': self.correct_lieu,
        }
        
        correction_func = corrections_map.get(field_name)
        if correction_func:
            corrected = correction_func(text)
            if corrected != text:
                print(f"✏️  Correction [{field_name}]: '{text}' → '{corrected}'")
            return corrected
        
        return text
    
    def validate_extraction(self, data: Dict) -> Dict:
        """Valide et signale les champs suspects"""
        validation_results = {}
        
        # Vérifier la date
        if 'Date' in data and data['Date'].get('text'):
            date_text = data['Date']['text']
            if not re.match(r'\d{2}/\d{2}/\d{4}', date_text):
                validation_results['Date'] = 'Format invalide'
        
        # Vérifier le montant MICR (doit contenir uniquement chiffres et :)
        if 'Ligne_MICR' in data and data['Ligne_MICR'].get('text'):
            micr = data['Ligne_MICR']['text']
            if re.search(r'[a-zA-Z]', micr):
                validation_results['Ligne_MICR'] = 'Contient des lettres'
        
        # Vérifier cohérence montant lettres vs chiffres (à implémenter si nécessaire)
        
        return validation_results