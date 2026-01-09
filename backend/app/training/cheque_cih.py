import re
import pandas as pd
import os
import random
import base64
from playwright.sync_api import sync_playwright
from pathlib import Path
from PIL import Image
import io

print("Script de génération des images de chèques (v3 Playwright) démarré...")

# --- NOUVELLE FONCTION : Créer le montant avec le remplissage ---
def format_montant_lettres(montant_str):
    """
    Encadre le montant en lettres avec des tirets de remplissage
    et met le montant en gras (<strong>).
    """
    # Caractère de remplissage
    FILL_CHAR = '_ ' 
    
    # Remplissage avant et après (ajustez 10 et 60 selon le besoin visuel)
    prefix = FILL_CHAR * 0
    suffix = FILL_CHAR * 0
    
    # Remplacement des espaces par des espaces insécables HTML (&nbsp;) 
    # pour éviter les sauts de ligne si le texte est long.
    montant_formatted = montant_str.strip().replace(' ', '&nbsp;') 
    
    # Chaîne finale : Remplissage, Montant en gras (<strong>), Remplissage
    # Le texte arabe est retiré ici car il est déjà dans le template HTML.
    return f"{prefix}&nbsp;<strong>{montant_formatted}</strong>&nbsp;{suffix} "

# --- NOUVELLE FONCTION : Génération Ligne MICR ---
def generer_ligne_micr(cheque_num, code_banque, code_agent, num_compte, cle_rib):
    """
    Génère la ligne MICR E-13B standard.
    Format: TRANSIT chequen° TRANSIT  banque+guichet  ON_US num_compte ON_US cle_rib ON_US
    """
    # Caractères spéciaux MICR E-13B
    TRANSIT = "⑆"  # U+2446
    ON_US = "⑇"    # U+2447

    try:
        # Assurer que les données sont des strings et paddées
        cheque_str = str(cheque_num).zfill(7)
        transit_str = f"{str(code_banque).zfill(3)}{str(code_agent).zfill(3)}"
        # Insère ON_US entre le numéro de compte et la clé RIB
        compte_part = str(num_compte).zfill(16)
        cle_part = str(cle_rib).zfill(2)
        compte_str = f"{compte_part}{ON_US}{cle_part}"
        
        # Formatage final
        return f"{TRANSIT}{cheque_str}{TRANSIT} {transit_str} {ON_US}{compte_str}{ON_US}"
        
    except Exception as e:
        print(f"!!! Erreur lors de la génération MICR: {e}")
        return ""



# --- Fonction helper pour convertir l'image et enlever le fond (inchangée) ---
def image_to_base64_uri(image_path):
    """
    Ouvre une image, rend son fond (pixels blancs/presque blancs) transparent,
    et la convertit en data URI base64 au format PNG.
    """
    if not os.path.exists(image_path):
        print(f"!!! Erreur : Fichier signature non trouvé : {image_path}")
        return ""
    
    try:
        # Ouvre l'image avec PIL
        img = Image.open(image_path)
        
        # --- SUPPRIMÉ LE RECADRAGE ---
        # On garde l'image telle quelle
        
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        
        WHITE_THRESHOLD = 230 
        
        for item in datas:
            if item[0] > WHITE_THRESHOLD and item[1] > WHITE_THRESHOLD and item[2] > WHITE_THRESHOLD:
                newData.append((255, 255, 255, 0))  # fond transparent
            else:
                newData.append(item)
        
        img.putdata(newData)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        
        img_bytes = img_byte_arr.getvalue()
        encoded_string = base64.b64encode(img_bytes).decode('utf-8')
        
        return f"data:image/png;base64,{encoded_string}"
    
    except Exception as e:
        print(f"!!! Erreur lors du traitement de l'image {image_path}: {e}")
        return ""



# --- 1. CONFIGURATION ---
PATH_TRANSACTIONS = "backend/app/data/transactions_cheques.csv"
PATH_OUTPUT_IMAGES = "backend/app/data/cheques/cih"
PATH_TEMPLATES_ROOT = "backend/app/data/cheques_templates" 

# Chemins vers vos templates HTML (assurez-vous qu'ils sont corrects)
TEMPLATE_PATHS = {
    "007": os.path.join(PATH_TEMPLATES_ROOT, "TIJARI Cheque/cheque.html"),
    "145": os.path.join(PATH_TEMPLATES_ROOT, "BCP Cheque/cheque.html"),
    "230": os.path.join(PATH_TEMPLATES_ROOT, "cih cheque/cheque.html")
}

# S'assurer que les dossiers existent
os.makedirs(PATH_OUTPUT_IMAGES, exist_ok=True)

try:
    # --- VÉRIFICATION DU TEMPLATE CIH UNIQUEMENT ---
    code_cih = "230"
    path_cih = TEMPLATE_PATHS.get(code_cih)
    
    if not path_cih or not os.path.exists(path_cih):
        raise FileNotFoundError(f"Template HTML pour CIH (code {code_cih}) non trouvé à : {path_cih}")
    
    css_path_cih = os.path.join(os.path.dirname(path_cih), "style.css")
    if not os.path.exists(css_path_cih):
        raise FileNotFoundError(f"Fichier style.css manquant pour CIH (code {code_cih}) à : {css_path_cih}")

    print("✅ Template CIH (230) vérifié.")
    
    df_transactions = pd.read_csv(PATH_TRANSACTIONS)
    print(f"✅ {len(df_transactions)} transactions chargées")
    
    # --- 2. LOGIQUE DE GÉNÉRATION (PLAYWRIGHT) ---
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print(f"🚀 Démarrage de Playwright (Chromium)...")

        generated_count = 0 

        for _, transaction in df_transactions.iterrows():
            
            if str(transaction['Code_Banque']) != "230":
                continue 
            
            nom_fichier_sortie = f"cheque_trans_{transaction['ID_Transaction']}.png"
            chemin_sortie = os.path.join(PATH_OUTPUT_IMAGES, nom_fichier_sortie)
            
            try:
                template_path = TEMPLATE_PATHS.get(str(transaction['Code_Banque']))
                
                if not template_path:
                    print(f"⚠️ Pas de template pour Code Banque {transaction['Code_Banque']}. Transaction {transaction['ID_Transaction']} ignorée.")
                    continue
                    
                with open(template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # --- Remplacement des placeholders ---
                
                # Montant en chiffres
                html_content = html_content.replace("PLACEHOLDER_MONTANT_CHIFFRES", str(transaction['Montant_Chiffres']))
                
                # Montant en lettres (Logique de remplissage)
                montant_lettres_str = str(transaction['Montant_Lettres'])
                montant_lettres_full = format_montant_lettres(montant_lettres_str)
                
                # Remplacement du placeholder FULL par la chaîne formatée.
                html_content = html_content.replace("PLACEHOLDER_MONTANT_LETTRES_FULL", montant_lettres_full)
                
                # Autres remplacements
                html_content = html_content.replace("PLACEHOLDER_BENEFICIAIRE", str(transaction['Nom_Beneficiaire']))
                html_content = html_content.replace("PLACEHOLDER_LIEU", str(transaction['Lieu_Emission']))
                html_content = html_content.replace("PLACEHOLDER_DATE", str(transaction['Date_Emission']))
                
                # ✅ AJOUTÉ : Remplacement des infos agence
                html_content = html_content.replace("PLACEHOLDER_AGENCE_ADRESSE", str(transaction['Agence_Adresse']))
                html_content = html_content.replace("PLACEHOLDER_AGENCE_TEL", str(transaction['Agence_Telephone']))

                # ✅ SUPPRIMÉ : Ce placeholder n'est pas dans le HTML
                # html_content = html_content.replace("PLACEHOLDER_NOM_EMETTEUR", str(transaction['Nom_Emetteur']))
                
                # Remplacements existants (Num Compte et Num Cheque)
                html_content = html_content.replace("PLACEHOLDER_NUM_COMPTE", str(transaction['Numero_Compte']))
                html_content = html_content.replace("PLACEHOLDER_NUM_CHEQUE", str(transaction['Numero_Cheque_Emetteur']))

                # NOUVEAU REMPLACEMENT : Ligne MICR
                micr_line = generer_ligne_micr(
                    transaction['Numero_Cheque_Emetteur'],
                    transaction['Code_Banque'],
                    transaction['Code_Agent'],
                    transaction['Numero_Compte'],
                    transaction['Cle_RIB']
                )
                html_content = html_content.replace("PLACEHOLDER_MICR", micr_line)

                # Remplacement de la signature (inchangé)
                signature_dir_path = transaction.get('Signature_Path_Genuine')
                signature_base64_uri = ""
                
                if signature_dir_path and isinstance(signature_dir_path, str) and os.path.isdir(signature_dir_path):
                    try:
                        image_files = [f for f in os.listdir(signature_dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        
                        if image_files:
                            chosen_image_name = random.choice(image_files)
                            signature_file_path = os.path.join(signature_dir_path, chosen_image_name)
                            signature_base64_uri = image_to_base64_uri(signature_file_path)
                        else:
                            print(f"⚠️ Pas de fichiers image (.png/.jpg) trouvés dans {signature_dir_path} pour Trans {transaction['ID_Transaction']}.")
                    
                    except Exception as e:
                        print(f"❌ Erreur en listant les signatures dans {signature_dir_path}: {e}")

                else:
                    if signature_dir_path and isinstance(signature_dir_path, str):
                         print(f"⚠️ Chemin de signature '{signature_dir_path}' n'est pas un dossier valide pour Trans {transaction['ID_Transaction']}.")
                    elif not signature_dir_path or not isinstance(signature_dir_path, str):
                         print(f"⚠️ Chemin de signature manquant/invalide (non-string) pour Trans {transaction['ID_Transaction']}.")

                html_content = html_content.replace("PLACEHOLDER_SIGNATURE_IMG", signature_base64_uri)
                # --- Fin des remplacements ---

                template_dir_abs = os.path.abspath(os.path.dirname(template_path))
                temp_html_path = os.path.join(template_dir_abs, f"temp_cheque_{transaction['ID_Transaction']}.html")

                with open(temp_html_path, 'w', encoding='utf-8') as tf:
                    tf.write(html_content)

                temp_uri = Path(temp_html_path).resolve().as_uri()
                page.goto(temp_uri, wait_until='load')
                page.set_viewport_size({"width": 833, "height": 429}) 
                page.screenshot(path=chemin_sortie)

                try:
                    os.remove(temp_html_path)
                except Exception:
                    pass

                print(f"✅ Image CIH générée : {nom_fichier_sortie}")
                generated_count += 1

            except Exception as e:
                print(f"❌ Erreur lors de la génération de {nom_fichier_sortie}: {e}")
        
        browser.close()
        print(f"👍 Génération terminée. {generated_count} chèque(s) CIH ont été générés.")

except Exception as e:
    print(f"❌ ERREUR... {e}")
    if 'browser' in locals() and browser.is_connected():
        browser.close()