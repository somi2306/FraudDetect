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
        
        # Noms marocains courants - DICTIONNAIRE ÉTENDU
        self.common_names = {
            'AHMED': ['Ahmed', 'Ahrned', 'Ahrnet', 'Ahmet', 'Ahmëd', 'Ahined'],
            'MOHAMMED': ['Mohammed', 'Mohanned', 'Mohanmed', 'Mohanrned', 'Moharnmed', 'Mohanamed', 'Mohamrned'],
            'HASSAN': ['Hassan', 'Hassar', 'Hassarn', 'Hassen', 'Hassane'],
            'YOUSSEF': ['Youssef', 'Yousset', 'Yousscf', 'Yousseff', 'Youssëf', 'Yousscff'],
            'KARIM': ['Karim', 'Kariim', 'Karirn', 'Kariïm', 'Karnn'],
            'FATIMA': ['Fatima', 'Fatiima', 'Fatirna', 'Fatîma', 'Fatiïma', 'Fatiina'],
            'AYOUB': ['Ayoub', 'Ayouo', 'Ayouë', 'Ayouï', 'Ayouö'],
            'NABIL': ['Nabil', 'Nacig', 'Nabig', 'Nacil', 'Nabif', 'Nabiï', 'Nabii'],
            'BADAOUI': ['Badaoui', 'Badacsui', 'Badasui', 'Badaowi', 'Badacui', 'Badaouï'],
            'MOUDSAID': ['Moudsaid', 'Moudsaïd', 'Moudsaîd', 'Moudssaid'],
            'OUM': ['Oum', 'oum', 'OUM', 'Ourn', 'Ourm'],
            'ESSAAD': ['Essaad', 'essaad', 'ESSAAD', 'Fsaad', 'Cssaad', 'saaad'],
            'MEFTAH': ['Meftah', 'meftah', 'MEFTAH', 'Mleftak', 'Meftak', 'Mieftak'],
            'RACHID': ['Rachid', 'Rachîd', 'Rachiid', 'Rachiïd', 'Rachïd'],
            'SAID': ['Said', 'Saïd', 'Saîd', 'Saiid', 'Saïïd'],
            'KHALID': ['Khalid', 'Khalîd', 'Khaliid', 'Khaliïd'],
            'OMAR': ['Omar', 'Ommar', 'Ornar', 'Ômar'],
            'ALI': ['Ali', 'Alï', 'Alî', 'Aii'],
            'SALAH': ['Salah', 'Saleh', 'Saloh', 'Salàh'],
            'ANAS': ['Anas', 'Anass', 'Anàs', 'Anâs'],
            'ZAKARIA': ['Zakaria', 'Zakarïa', 'Zakarîa', 'Zakariya'],
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
        """Corrige le nom du bénéficiaire - ALGORITHME AMÉLIORÉ"""
        if not text:
            return text
        
        # Nettoyer les caractères parasites mais GARDER les espaces
        text = text.lstrip("'\"`@#*_{").rstrip("_- .,")
        
        # Supprimer caractères spéciaux mais garder lettres et espaces
        text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', text)
        
        # Normaliser les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Séparer les mots
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Ignorer mots très courts (bruit)
            if len(word) < 2:
                continue
            
            # Chercher dans le dictionnaire avec seuil plus bas pour mieux matcher
            corrected = self.find_similar_word(word, self.common_names, threshold=0.50)
            
            # Si pas trouvé dans dictionnaire, garder le mot mais capitaliser
            if corrected == word:
                # Capitaliser proprement (première lettre majuscule)
                corrected = word.capitalize()
            else:
                # Mot trouvé dans dictionnaire, capitaliser
                corrected = corrected.capitalize()
            
            corrected_words.append(corrected)
        
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
        """
        Corrige la ligne MICR - FORMAT FIXE STRICT
        
        FORMAT OBLIGATOIRE: 7 chiffres + 6 chiffres + 18 chiffres
        Exemple: 1000001 230807 220000000000000003
        
        Structure:
        - Groupe 1 (7 chiffres): Numéro de chèque
        - Groupe 2 (6 chiffres): Code agence/banque
        - Groupe 3 (18 chiffres): Numéro de compte
        
        PROBLÈMES COURANTS:
        - # lus comme 4 au début
        - Chiffres mal séparés ou collés
        """
        if not text:
            return text
        
        # Nettoyer: garder uniquement chiffres
        cleaned = re.sub(r'[^\d]', '', text)
        
        if not cleaned:
            return text
        
        # CORRECTION DES # AU DÉBUT
        # Si commence par 4/44, c'est probablement des #
        if cleaned.startswith('44') and len(cleaned) > 31:
            cleaned = cleaned[2:]  # Enlever 44
        elif cleaned.startswith('4') and len(cleaned) > 31:
            cleaned = cleaned[1:]  # Enlever 1 seul 4
        
        # FORMAT ATTENDU: 7 + 6 + 18 = 31 chiffres minimum
        total_expected = 31
        
        if len(cleaned) < total_expected:
            # Pas assez de chiffres, compléter avec des 0
            cleaned = cleaned.ljust(total_expected, '0')
        elif len(cleaned) > total_expected:
            # Trop de chiffres, prendre les premiers 31
            cleaned = cleaned[:total_expected]
        
        # DÉCOUPER AU FORMAT FIXE: 7-6-18
        groupe1 = cleaned[0:7]    # 7 chiffres (numéro chèque)
        groupe2 = cleaned[7:13]   # 6 chiffres (code agence)
        groupe3 = cleaned[13:31]  # 18 chiffres (compte)
        
        return f"{groupe1} {groupe2} {groupe3}"
    
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
        Corrige le montant en chiffres - ALGORITHME AMÉLIORÉ
        
        FORMAT RÉEL: ##MONTANT.XX##
        PROBLÈME: # → lu comme 4 par OCR
        
        EXEMPLES:
        - OCR: "47900.43" → RÉEL: "7900.43"  (## au début)
        - OCR: "46034.97" → RÉEL: "6034.97"
        - OCR: "44530.79" → RÉEL: "530.79"   (## → 44)
        
        RÈGLES:
        1. Montant réaliste: 10.00 à 999999.99 MAD
        2. Format: X.XX (toujours 2 décimales)
        3. Si commence par 4/44/444 → suspect (probablement des #)
        """
        if not text:
            return text
        
        # Nettoyer: garder chiffres et point
        cleaned = re.sub(r'[^\d.,]', '', text)
        cleaned = cleaned.replace(',', '.')
        
        if not cleaned:
            return ""
        
        # ========================================
        # CAS 1: POINT PRÉSENT
        # ========================================
        if '.' in cleaned:
            parts = cleaned.split('.')
            entier = parts[0]
            decimales = ''.join(parts[1:])[:2].ljust(2, '0')
            
            # DÉTECTION INTELLIGENTE DES #
            # Les # en début sont lus comme 4 ou 44
            
            # Si commence par 44 → presque certain que c'est ##
            if entier.startswith('44') and len(entier) > 4:
                entier = entier[2:]  # Enlever 44
            
            # Si commence par 4 et > 5 chiffres → probable que c'est #
            elif entier.startswith('4') and len(entier) > 5:
                entier = entier[1:]  # Enlever 1 seul 4
            
            # Si commence par 4, longueur 5, et 2ème chiffre est aussi 4
            # Ex: "47900" → probablement "7900" (4# au lieu de ##)
            elif entier.startswith('4') and len(entier) == 5 and entier[1] != '0':
                # Heuristique: si enlever le 4 donne un montant plus plausible
                # (entre 1000 et 9999 MAD)
                entier_test = entier[1:]
                if 1000 <= int(entier_test) <= 9999:
                    entier = entier_test
            
            # Sécurité: max 6 chiffres
            if len(entier) > 6:
                entier = entier[-6:]
            
            # Si vide ou invalide
            if not entier or int(entier) == 0:
                entier = '0'
            
            return f"{entier}.{decimales}"
        
        # ========================================
        # CAS 2: PAS DE POINT
        # ========================================
        
        # Les 2 derniers = décimales
        if len(cleaned) < 3:
            return cleaned
        
        entier = cleaned[:-2]
        decimales = cleaned[-2:]
        
        # Même logique anti-4
        if entier.startswith('44') and len(entier) > 4:
            entier = entier[2:]
        elif entier.startswith('4') and len(entier) > 5:
            entier = entier[1:]
        elif entier.startswith('4') and len(entier) == 5:
            entier_test = entier[1:]
            if 1000 <= int(entier_test) <= 9999:
                entier = entier_test
        
        if len(entier) > 6:
            entier = entier[-6:]
        
        if not entier or int(entier) == 0:
            entier = '0'
        
        return f"{entier}.{decimales}"
    
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
        """Valide et signale les champs suspects - AMÉLIORÉ"""
        validation_results = {}
        
        # Validation de la date
        if 'Date' in data and data['Date'].get('text_corrected'):
            date_text = data['Date']['text_corrected']
            if not re.match(r'\d{2}/\d{2}/\d{4}', date_text):
                validation_results['Date'] = '⚠️ Format invalide (attendu: JJ/MM/AAAA)'
        
        # Validation de la ligne MICR
        if 'Ligne_MICR' in data and data['Ligne_MICR'].get('text_corrected'):
            micr = data['Ligne_MICR']['text_corrected']
            
            # Vérifier pas de lettres
            if re.search(r'[a-zA-Z]', micr):
                validation_results['Ligne_MICR'] = '⚠️ Contient des lettres (devrait être numérique)'
            
            # Vérifier le format (3 groupes séparés par espaces)
            groups = micr.split()
            if len(groups) != 3:
                validation_results['Ligne_MICR'] = f'⚠️ Format suspect (trouvé {len(groups)} groupes, attendu 3)'
            
            # Vérifier les longueurs EXACTES: 7-6-18
            elif len(groups) == 3:
                if len(groups[0]) != 7 or len(groups[1]) != 6 or len(groups[2]) != 18:
                    validation_results['Ligne_MICR'] = f'⚠️ Longueurs incorrectes (trouvé: {len(groups[0])}-{len(groups[1])}-{len(groups[2])}, attendu: 7-6-18)'
        
        # Validation du montant en chiffres
        if 'Montant_Chiffres' in data and data['Montant_Chiffres'].get('text_corrected'):
            montant = data['Montant_Chiffres']['text_corrected']
            if not re.match(r'^\d+\.\d{2}$', montant):
                validation_results['Montant_Chiffres'] = '⚠️ Format invalide (attendu: XXXX.XX)'
            else:
                # Vérifier plage réaliste
                montant_val = float(montant)
                if montant_val < 10 or montant_val > 1000000:
                    validation_results['Montant_Chiffres'] = f'⚠️ Montant suspect ({montant} MAD)'
        
        # Validation du montant en lettres
        if 'Montant_Lettres' in data and data['Montant_Lettres'].get('text_corrected'):
            montant_lettres = data['Montant_Lettres']['text_corrected']
            
            # Vérifier présence de DIRHAMS
            if 'DIRHAM' not in montant_lettres:
                validation_results['Montant_Lettres'] = '⚠️ Monnaie non détectée (DIRHAMS manquant)'
            
            # Vérifier cohérence avec montant chiffres
            if 'Montant_Chiffres' in data and data['Montant_Chiffres'].get('text_corrected'):
                montant_chiffres = float(data['Montant_Chiffres']['text_corrected'])
                
                # Conversion simple lettres → chiffres (approximatif)
                montant_estime = self._estimate_amount_from_text(montant_lettres)
                
                if montant_estime and abs(montant_chiffres - montant_estime) / montant_chiffres > 0.1:
                    validation_results['Coherence'] = f'⚠️ INCOHÉRENCE: Chiffres={montant_chiffres} MAD vs Lettres≈{montant_estime} MAD'
        
        return validation_results
    
    def _estimate_amount_from_text(self, text: str) -> Optional[float]:
        """Estime le montant à partir du texte en lettres (approximatif)"""
        text = text.upper()
        
        # Dictionnaire de conversion
        nombres = {
            'UN': 1, 'DEUX': 2, 'TROIS': 3, 'QUATRE': 4, 'CINQ': 5,
            'SIX': 6, 'SEPT': 7, 'HUIT': 8, 'NEUF': 9, 'DIX': 10,
            'VINGT': 20, 'TRENTE': 30, 'QUARANTE': 40, 'CINQUANTE': 50,
            'SOIXANTE': 60, 'CENT': 100, 'MILLE': 1000
        }
        
        total = 0
        current = 0
        
        for word in text.split():
            if word in nombres:
                val = nombres[word]
                if val >= 100:
                    current = current * val if current else val
                else:
                    current += val
            elif word == 'MILLE':
                total += current * 1000 if current else 1000
                current = 0
        
        total += current
        
        return float(total) if total > 0 else None