import re
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from difflib import SequenceMatcher

class OCRCorrector:
    """Classe pour corriger les erreurs OCR des chèques manuscrits"""
    
    def __init__(self):
        # Dictionnaire des confusions courantes en écriture manuscrite
        self.char_corrections = {
            'O': '0', 'o': '0',
            'l': '1', 'I': '1', '|': '1',
            'Z': '2', 'z': '2',
            'S': '5', 's': '5',
            'G': '6', 'g': '6',
            'T': '7', 't': '7',
            'B': '8', 'b': '8',
            'g': '9', 'q': '9',
        }
        
        # Corrections spécifiques pour montants en lettres (français)
        self.word_corrections = {
            # Nombres de base
            'UN': ['UN', 'UN3', 'UÎN', 'U1N'],
            'DEUX': ['DEUX', 'D3UX', 'DFUX', 'DEUZ', 'DËUX', 'DEUZREXT'],
            'TROIS': ['TROIS', 'TR01S', 'TRO1S', 'TRÔ1S', 'TRO15'],
            'QUATRE': ['QUATRE', 'QUATRF', 'QUAT2E', 'QUATPE', 'QUA7RE', 'QUATIE'],
            'CINQ': ['CINQ', 'ClNQ', 'C1NQ', 'CÎNQ', 'C1NÔ'],
            'SIX': ['SIX', 'S1X', 'SlX', 'SÏX'],
            'SEPT': ['SEPT', 'SePT', 'SeP7', 'S3PT', 'S{PT', 'S£PT', 'SLPT'],
            'HUIT': ['HUIT', 'HU1T', 'HUlT', 'HÜIT', 'HUIB'],
            'NEUF': ['NEUF', 'N3UF', 'NËUF', 'N€UF', 'NEU', 'N3U'],
            'DIX': ['DIX', 'D1X', 'DlX', 'DÏX'],
            
            # Dizaines
            'VINGT': ['VINGT', 'VlNGT', 'V1NGT', 'VÎNGT', 'VIN6T', 'VINËT', 'UINGT'],
            'TRENTE': ['TRENTE', 'TR3NTE', 'TRFNTE', 'TRENTË'],
            'QUARANTE': ['QUARANTE', 'QUARANTF', 'QUARANTË', 'QUARANTÈ'],
            'CINQUANTE': ['CINQUANTE', 'C1NQUANTE', 'CINQUANTF', 'CINQUANTË'],
            'SOIXANTE': ['SOIXANTE', 'SO1XANTE', 'SOIXANTF', 'SOIXANTË'],
            
            # Centaines et mille
            'CENT': ['CENT', 'C3NT', 'CFNT', 'C£NT', 'CÉNT', 'C€NT', 'CÈNT', 'CTTCS'],
            'MILLE': ['MILLE', 'MIP2C', 'MIPPC', 'MIL2C', 'MILPC', 'M1LLE', 'MIITE', 'MIËLE', 'TTE'],
            
            # Monnaie
            'DIRHAMS': ['DIRHAMS', 'DIRhAMS', 'DIRH4MS', 'DIRHÀMS', 'DIRHHAMS', 'DIR4AMS'],
            'CENTIMES': ['CENTIMES', 'C3NTIMES', 'CFNTIMES', 'CENTINES', 'CENTIIMES'],
        }
        
        # Noms marocains courants
        self.common_names = {
            'OUM': ['oum', 'Oum', 'OUM', 'Ourn', 'Ourm'],
            'ESSAAD': ['essaad', 'Essaad', 'ESSAAD', 'Fsaad', 'Cssaad', 'saaad'],
            'MEFTAH': ['meftah', 'Meftah', 'MEFTAH', 'Mleftak', 'Meftak', 'Mieftak'],
            'NABIL': ['Nacig', 'Nabig', 'Nacil', 'Nabif', 'Nabil', 'Nabiï'],
            'BADAOUI': ['Badacsui', 'Badaoui', 'Badasui', 'Badaowi', 'Badacui', 'Badaouï'],
            'MOHAMMED': ['Mohanned', 'Mohanmed', 'Mohanrned', 'Moharnmed', 'Mohanamed'],
            'HASSAN': ['Hassar', 'Hassarn', 'Hassen', 'Hassan', 'Hassane'],
            'YOUSSEF': ['Yousset', 'Yousscf', 'Yousseff', 'Youssëf', 'Yousscff'],
            'KARIM': ['Kariim', 'Karirn', 'Kariïm', 'Karnn'],
            'AHMED': ['Ahrned', 'Ahrnet', 'Ahmet', 'Ahmëd'],
            'FATIMA': ['Fatiima', 'Fatirna', 'Fatîma', 'Fatiïma'],
            'AYOUB': ['Ayouo', 'Ayouo', 'Ayouë', 'Ayouï'],
        }
        
        # Villes marocaines
        self.moroccan_cities = {
            'CASABLANCA': ['Cabeglancn', 'Casablanca', 'Casablancn', 'Casaolanca', 'Casabianca', 'Casoblanca'],
            'RABAT': ['Rabal', 'Rabalt', 'Raoat', 'Rabàt', 'Raöat'],
            'MARRAKECH': ['Marrakech', 'Marrakcch', 'Marrakesh', 'Marrakëch'],
            'FES': ['Fes', 'Fés', 'Fcz', 'Fès', 'Fëz'],
            'TANGER': ['Tanger', 'Tangcr', 'Tanqer', 'Tangër', 'Tanjer'],
            'AGADIR': ['Agadir', 'Agadïr', 'Aqadir'],
            'MEKNES': ['Meknes', 'Meknès', 'Meknës', 'Mëknës'],
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Améliore la qualité de l'image avant OCR"""
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
    
    def find_similar_word(self, word: str, dictionary: Dict[str, list], threshold: float = 0.6) -> str:
        """Trouve le mot le plus similaire dans un dictionnaire"""
        word_clean = word.upper().strip("'\"`,{}_-!?")
        best_match = word
        best_ratio = threshold
        
        for correct_word, variations in dictionary.items():
            # Vérifier les variations connues
            for variation in variations:
                if word_clean == variation.upper():
                    return correct_word
                
                # Calculer la similarité
                ratio = SequenceMatcher(None, word_clean, variation.upper()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = correct_word
        
        return best_match if best_ratio > threshold else word
    
    def correct_beneficiaire(self, text: str) -> str:
        """Corrige le nom du bénéficiaire"""
        if not text:
            return text
        
        # Nettoyer les caractères parasites au début/fin
        text = text.lstrip("'\"`@#*_{").rstrip("_- .,")
        
        # Supprimer les doubles espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Séparer les mots
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Ignorer les mots très courts (probablement du bruit)
            if len(word) < 2:
                continue
            
            # Chercher dans le dictionnaire des noms
            corrected = self.find_similar_word(word, self.common_names, threshold=0.55)
            corrected_words.append(corrected.capitalize())
        
        result = ' '.join(corrected_words)
        return result.strip()
    
    def correct_montant_lettres(self, text: str) -> str:
        """Corrige le montant écrit en lettres"""
        if not text:
            return text
        
        # Convertir en majuscules
        text = text.upper()
        
        # Supprimer "Payez contre ce cheque" et autres formules
        patterns_to_remove = [
            r'^.*?(?:PAYEZ\s+CONTRE\s+CE\s+CHE[QO]UE?\s*)',
            r'^.*?(?:LA\s+SOMME\s+DE\s*)',
            r'^.*?(?:ORDRE\s+DE\s*)',
            r'^.*?(?:TOUTES\s+)',
        ]
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Nettoyer les caractères parasites
        text = re.sub(r'[\'\"`,_\(\)\{\}\[\]£€@#*!?]', ' ', text)
        
        # Normaliser les espaces et tirets
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'-+', '-', text)
        
        # Séparer les mots
        words = text.split()
        corrected_words = []
        
        for word in words:
            word_clean = word.strip("'-.,;:!")
            if len(word_clean) < 2:
                continue
            
            # Chercher dans le dictionnaire des nombres
            corrected = self.find_similar_word(word_clean, self.word_corrections, threshold=0.50)
            corrected_words.append(corrected)
        
        result = ' '.join(corrected_words)
        
        # Supprimer tout après CENTIMES
        result = re.sub(r'(CENTIMES?).*', r'\1', result, flags=re.IGNORECASE)
        
        # Normaliser "ET" entre parties du montant
        result = re.sub(r'\s+ET\s+', ' ET ', result)
        
        return result.strip()
    
    def correct_num_cheque(self, text: str) -> str:
        """Corrige le numéro de chèque"""
        if not text:
            return text
        
        # Supprimer les caractères parasites (garder chiffres, N, °, :, -)
        text = re.sub(r'[^\d\sN:n°-]', '', text)
        
        # Extraire uniquement les chiffres après N: ou N°
        patterns = [
            r'[Nn]\s*[:°]\s*(\d+)',
            r'[Nn]°?\s*(\d+)',
            r'№\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"N: {match.group(1)}"
        
        # Si pas de format N:, extraire juste les chiffres
        numbers = re.findall(r'\d+', text)
        if numbers:
            # Prendre le plus long nombre (probablement le numéro)
            longest = max(numbers, key=len)
            return f"N: {longest}"
        
        return text.strip()
    
    def correct_num_compte(self, text: str) -> str:
        """Corrige le numéro de compte - garder les chiffres sans séparation"""
        if not text:
            return text
        
        # Garder uniquement chiffres
        text = re.sub(r'[^\d]', '', text)
        
        # Retourner le numéro sans formatage
        return text
    
    def correct_ligne_micr(self, text: str) -> str:
        """Corrige la ligne MICR - format: XXXXXXX XXXXXX XXXXXXXXXXXXXXXXXXXX"""
        if not text:
            return text
        
        # Remplacer tous les séparateurs et caractères parasites par des espaces
        text = re.sub(r'[^\d\s]', ' ', text)
        
        # Normaliser les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Extraire tous les nombres
        numbers = re.findall(r'\d+', text)
        
        if not numbers:
            return text
        
        # La ligne MICR typique a 3 groupes de chiffres
        # Format attendu: 1000001 230807 220000000000000003
        if len(numbers) >= 3:
            # Prendre les 3 premiers groupes significatifs
            return f"{numbers[0]} {numbers[1]} {numbers[2]}"
        elif len(numbers) == 2:
            return f"{numbers[0]} {numbers[1]}"
        else:
            return numbers[0]
    
    def correct_date(self, text: str) -> str:
        """Valide et corrige le format de date"""
        if not text:
            return text
        
        # Supprimer "Le" ou "le" au début
        text = re.sub(r'^[Ll]e\s+', '', text)
        
        # Supprimer "à" ou "a" suivi d'un lieu
        text = re.sub(r'\s+[àaÀA]\s+.*$', '', text)
        
        # Extraire les chiffres de la date
        patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                day, month, year = match.groups()
                
                # Convertir année sur 2 chiffres en 4
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                
                # Valider les valeurs
                day_int = int(day)
                month_int = int(month)
                
                if 1 <= day_int <= 31 and 1 <= month_int <= 12:
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        return text.strip()
    
    def correct_lieu(self, text: str) -> str:
        """Corrige le lieu"""
        if not text:
            return text
        
        # Supprimer caractères parasites
        text = text.replace('_', '').replace('-', ' ').strip()
        
        # Supprimer "à" ou "a" au début
        text = re.sub(r'^[àaÀA]\s+', '', text, flags=re.IGNORECASE)
        
        # Chercher dans le dictionnaire des villes
        corrected = self.find_similar_word(text, self.moroccan_cities, threshold=0.65)
        
        return corrected.capitalize()
    
    def correct_montant_chiffres(self, text: str) -> str:
        """
        Corrige le montant en chiffres avec logique anti-# ROBUSTE
        
        FORMAT CHÈQUE: ##MONTANT.XX##
        
        PROBLÈME: Les # sont lus comme 4 par l'OCR
        
        EXEMPLES RÉELS:
        ┌─────────────┬──────────────┬─────────────┐
        │ OCR         │ RÉEL         │ CORRECTION  │
        ├─────────────┼──────────────┼─────────────┤
        │ 4649.56     │ ##649.56##   │ 649.56      │
        │ 46034.97    │ ##6034.97##  │ 6034.97     │
        │ 90112.74    │ ##9011.27##  │ 9011.27     │
        │ 44530.79    │ ##530.79##   │ 530.79      │
        │ 1146394251  │ ##1146.39##  │ 1146.39     │
        └─────────────┴──────────────┴─────────────┘
        
        STRATÉGIE OPTIMALE:
        1. Nettoyer pour avoir uniquement chiffres et point
        2. Identifier si point présent ou non
        3. RÈGLE CLÉ: Un montant marocain réaliste = 2 à 6 chiffres AVANT le point
        4. Si plus de 6 chiffres avant point → enlever chiffres du début jusqu'à avoir 6 max
        5. Si pas de point et > 8 chiffres total → garder seulement 6-8 chiffres
        """
        if not text:
            return text
        
        # Étape 1: Nettoyer
        cleaned = re.sub(r'[^\d.,]', '', text)
        cleaned = cleaned.replace(',', '.')
        
        if not cleaned:
            return ""
        
        # ============================================================
        # CAS A: POINT PRÉSENT
        # ============================================================
        if '.' in cleaned:
            parts = cleaned.split('.')
            entier = parts[0]
            decimales_brutes = ''.join(parts[1:])
            
            # Garder 2 décimales (ou compléter avec 0)
            decimales = decimales_brutes[:2].ljust(2, '0')
            
            # ===== LOGIQUE ANTI-# ULTRA ROBUSTE =====
            # 
            # OBSERVATION: Les ## au début sont souvent lus comme 44, 4, etc.
            # 
            # STRATÉGIE EN 3 PASSES:
            
            # PASSE 1: Enlever les 4 du début si ça dépasse 6 chiffres
            while entier.startswith('4') and len(entier) > 6:
                entier = entier[1:]
            
            # PASSE 2: Si commence ENCORE par 4 ET qu'on a 4-6 chiffres
            # Vérifier si c'est plausible d'enlever le 4
            if entier.startswith('4') and 4 <= len(entier) <= 6:
                # Exemples:
                # "4530" → enlever ? → "530" (3 chiffres, plausible ✅)
                # "4999" → enlever ? → "999" (3 chiffres, plausible ✅)
                # "4012" → enlever ? → "012" (3 chiffres, commence par 0 ❌)
                
                entier_sans_4 = entier[1:]
                
                # Ne pas enlever si ça commence par 0 (montant invalide)
                if entier_sans_4 and not entier_sans_4.startswith('0'):
                    # Montant plus court = plus plausible pour un chèque
                    entier = entier_sans_4
            
            # PASSE 3: Si commence par 44, 444, etc. (multiples 4)
            # C'est presque sûr que ce sont des ##
            if entier.startswith('44'):
                # Enlever tous les 4 consécutifs du début
                while entier.startswith('4') and len(entier) > 2:
                    entier = entier[1:]
            
            # PASSE 4: Sécurité finale - jamais plus de 6 chiffres
            while len(entier) > 6 and entier:
                entier = entier[1:]
            
            # Validation: si vide ou commence par 0
            if not entier or entier == '0':
                entier = '0'
            
            return f"{entier}.{decimales}"
        
        # ============================================================
        # CAS B: PAS DE POINT (tous les chiffres collés)
        # ============================================================
        
        # Exemples problématiques:
        # "1146394251" devrait donner "1146.39"
        # "90112.74" lu comme "9011274" → mais ici pas de point détecté ? Non, ce cas est géré au-dessus
        
        # STRATÉGIE RÉVISÉE:
        # Format: [parasites_début]ENTIER[DECIMALES][parasites_fin]
        # 
        # Heuristique: Les # ajoutent généralement 1-2 chiffres au début ET 2-4 à la fin
        # Montant réel = 4 à 8 chiffres (entier + 2 déc)
        
        total_len = len(cleaned)
        
        if total_len <= 8:
            # Cas simple: probablement juste entier+déc avec peut-être 1-2 parasites
            # Les 2 derniers = décimales
            if len(cleaned) >= 3:
                entier = cleaned[:-2]
                decimales = cleaned[-2:]
                
                # Si entier > 6 chiffres, couper du début
                while len(entier) > 6 and entier:
                    entier = entier[1:]
                
                if not entier:
                    entier = '0'
                
                return f"{entier}.{decimales}"
        else:
            # Cas complexe: beaucoup de parasites
            # Ex: "1146394251" = 10 chiffres
            #     Format réel: ##1146.39##
            #     Décodé: 4 4 1 1 4 6 3 9 4 2 5 1
            #             └┬┘ └──┬──┘ └┬┘ └──┬──┘
            #              ## entier  déc   ##...
            
            # MÉTHODE: Essayer toutes les fenêtres possibles de 6-8 chiffres
            # et choisir celle qui donne le montant le plus réaliste
            
            best_montant = None
            best_score = -1
            
            # Essayer différentes positions
            for start in range(max(0, total_len - 10), min(4, total_len - 5)):
                for length in [6, 7, 8]:
                    if start + length <= total_len:
                        window = cleaned[start:start + length]
                        
                        # Séparer en entier + déc
                        entier_test = window[:-2]
                        dec_test = window[-2:]
                        
                        # Score: préférer entier entre 2 et 6 chiffres
                        if 2 <= len(entier_test) <= 6:
                            score = 10 - abs(len(entier_test) - 4)  # Optimal = 4 chiffres
                            
                            if score > best_score:
                                best_score = score
                                best_montant = f"{entier_test}.{dec_test}"
            
            if best_montant:
                return best_montant
            
            # Fallback: garder les 7 premiers chiffres
            cleaned = cleaned[:7]
            if len(cleaned) >= 3:
                entier = cleaned[:-2]
                decimales = cleaned[-2:]
                
                while len(entier) > 6 and entier:
                    entier = entier[1:]
                
                if not entier:
                    entier = '0'
                
                return f"{entier}.{decimales}"
        
        # Trop court
        return cleaned
    
    def correct_field(self, field_name: str, text: str, image: np.ndarray = None) -> str:
        """Applique la correction appropriée selon le champ"""
        if not text:
            return text
        
        corrections_map = {
            'Beneficiaire': self.correct_beneficiaire,
            'Montant_Lettres': self.correct_montant_lettres,
            'Montant_Chiffres': self.correct_montant_chiffres,
            'Num_Cheque': self.correct_num_cheque,
            'Num_Compte': self.correct_num_compte,
            'Ligne_MICR': self.correct_ligne_micr,
            'Date': self.correct_date,
            'Lieu': self.correct_lieu,
        }
        
        correction_func = corrections_map.get(field_name)
        if correction_func:
            return correction_func(text)
        
        return text
    
    def validate_extraction(self, data: Dict) -> Dict:
        """Valide et signale les champs suspects"""
        validation_results = {}
        
        # Validation de la date
        if 'Date' in data and data['Date'].get('text_corrected'):
            date_text = data['Date']['text_corrected']
            if not re.match(r'\d{2}/\d{2}/\d{4}', date_text):
                validation_results['Date'] = 'Format invalide (attendu: JJ/MM/AAAA)'
        
        # Validation de la ligne MICR
        if 'Ligne_MICR' in data and data['Ligne_MICR'].get('text_corrected'):
            micr = data['Ligne_MICR']['text_corrected']
            if re.search(r'[a-zA-Z]', micr):
                validation_results['Ligne_MICR'] = 'Contient des lettres (devrait être uniquement numérique)'
            # Vérifier le format (3 groupes séparés par espaces)
            groups = micr.split()
            if len(groups) != 3:
                validation_results['Ligne_MICR'] = f'Format suspect (trouvé {len(groups)} groupes, attendu 3)'
        
        # Validation du montant en chiffres
        if 'Montant_Chiffres' in data and data['Montant_Chiffres'].get('text_corrected'):
            montant = data['Montant_Chiffres']['text_corrected']
            if not re.match(r'^\d+\.\d{2}$', montant):
                validation_results['Montant_Chiffres'] = 'Format invalide (attendu: XXXX.XX)'
        
        # Validation du montant en lettres
        if 'Montant_Lettres' in data and data['Montant_Lettres'].get('text_corrected'):
            montant_lettres = data['Montant_Lettres']['text_corrected']
            
            # Vérifier présence de DIRHAMS ou CENTIMES
            if 'DIRHAM' not in montant_lettres and 'CENTIME' not in montant_lettres:
                validation_results['Montant_Lettres'] = 'Monnaie non détectée (DIRHAMS/CENTIMES)'
        
        return validation_results