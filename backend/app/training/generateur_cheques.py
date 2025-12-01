import pandas as pd
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright 
from num2words import num2words
from PIL import Image
import os
from datetime import datetime
import random 
import time

# --- Configuration ---
TEMPLATE_DIR = '.' 
TEMPLATE_FILE = 'cheque.html' 
RIB_BP_PREFIX = "145" 
VILLE_EMISSION_FIXE = "Casablanca" 
CSV_CLIENTS_PATH = '../data/clients_training_map.csv'
CSV_BENEFICIAIRES_PATH = '../data/beneficiaires.csv'
OUTPUT_DIR = '../../../cheques_test' 
SIGNATURES_OUTPUT_DIR = os.path.join(os.path.abspath(OUTPUT_DIR), "signatures_transparentes")

# Assurez-vous que les répertoires de sortie existent
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SIGNATURES_OUTPUT_DIR, exist_ok=True)

# 1. Configuration de Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template(TEMPLATE_FILE)

# ----------------------------------------------------------------------
# --- Fonctions Utilitaires (Inchangées) ---
# ----------------------------------------------------------------------

def make_signature_transparent(image_path, output_path):
    """Rend le fond d'une image de signature transparent et sauvegarde en PNG (Nécessite PIL)."""
    try:
        img = Image.open(image_path).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            r, g, b, a = item
            # Si le pixel est blanc/très clair, le rendre transparent (alpha = 0)
            if r > 240 and g > 240 and b > 240:
                newData.append((255, 255, 255, 0))
            else:
                # Laisser les couleurs sombres opaques (Noir opaque)
                newData.append((0, 0, 0, 255)) 

        img.putdata(newData)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
    except FileNotFoundError:
        print(f"❌ Erreur: Image de signature non trouvée à l'emplacement: {image_path}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du traitement de l'image de signature : {e}")
        return None

def convertir_montant_en_lettres(montant):
    """Convertit le montant en Dirhams et Centimes en lettres (français - Nécessite num2words)."""
    
    montant_entier = int(montant)
    montant_decimal = int(round((montant - montant_entier) * 100))
    
    texte_lettres = ""
    
    if montant_entier > 0:
        dirhams_en_lettres = num2words(montant_entier, lang='fr')
        dirham_mot = "dirham" if montant_entier <= 1 else "dirhams"
        texte_lettres += f"{dirhams_en_lettres.upper()} {dirham_mot.upper()}"
        
    if montant_decimal > 0:
        centimes_en_lettres = num2words(montant_decimal, lang='fr')
        centimes_mot = "centime" if montant_decimal <= 1 else "centimes"
        
        separateur = " et " if montant_entier > 0 else ""
        texte_lettres += f"{separateur}{centimes_en_lettres.upper()} {centimes_mot.upper()}"
        
    if not texte_lettres:
        return "ZÉRO DIRHAMS"

    return texte_lettres

# === Fonction pour générer la ligne MICR ===
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
        cheque_str = str(cheque_num).zfill(7) # 7 chiffres pour le numéro de chèque
        
        # Le code banque (3) et le code agent (3) sont regroupés pour le "Transit"
        transit_str = f"{str(code_banque).zfill(3)}{str(code_agent).zfill(3)}" 
        
        # Le numéro de compte (16) et la clé RIB (2) sont combinés pour le "On Us"
        compte_part = str(num_compte).zfill(16)
        cle_part = str(cle_rib).zfill(2)
        
        # Formatage du champ "On Us" : num_compte + ON_US + cle_rib
        compte_cle_str = f"{compte_part}{ON_US}{cle_part}" 

        # Formatage final: chèque_num / banque+guichet / num_compte+cle_rib
        return f"{TRANSIT}{cheque_str}{TRANSIT} {transit_str} {ON_US}{compte_cle_str}{ON_US}"
        
    except Exception as e:
        print(f"!!! Erreur lors de la génération MICR: {e}")
        return ""


def generer_png(html_content, nom_fichier_png):
    """
    Convertit le contenu HTML en fichier PNG en utilisant Playwright (Chromium).
    Correction: S'assure que les styles sont chargés via un chemin absolu.
    """
    style_path = os.path.abspath(os.path.join(TEMPLATE_DIR, 'style1.css'))
    style_tag_relatif = '<link rel="stylesheet" href="style1.css">'
    style_tag_absolu = f'<link rel="stylesheet" href="file:///{style_path}">'
    
    html_content_with_absolute_css = html_content.replace(style_tag_relatif, style_tag_absolu)

    temp_html_path = os.path.join(OUTPUT_DIR, "temp_cheque_rendu.html")
    
    try:
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content_with_absolute_css) 

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            page.goto(f"file:///{os.path.abspath(temp_html_path)}") 
            page.wait_for_load_state("networkidle") 
            
            cheque_element = page.locator('.frame.board-13e72c2a5001')
            
            output_path = os.path.join(OUTPUT_DIR, nom_fichier_png)
            
            cheque_element.screenshot(path=output_path)
            
            browser.close()
            
        print(f"✅ Fichier généré : {nom_fichier_png}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PNG : {e}")
        print("Vérifiez que vous avez bien installé Playwright et les navigateurs.")
    finally:
        if os.path.exists(temp_html_path):
             os.remove(temp_html_path) 

# ----------------------------------------------------------------------
# --- FONCTION DE GÉNÉRATION AVEC LOGIQUE DE SOLDE ET BÉNÉFICIAIRE CIBLÉ (MISE À JOUR) ---
# ----------------------------------------------------------------------

def generer_cheque_client_cible(client_data, beneficiaires_df, template, base_sign_dir, SIGNATURES_OUTPUT_DIR, current_balance, beneficiaire_id_cible):
    """
    Génère un seul chèque pour les données du client donné, pour un bénéficiaire CIBLE, 
    en utilisant le solde actuel comme montant maximum.
    """
    
    client_id = client_data['ID_CLIENT_SYNTH'] 
    client_rib = str(client_data['RIB']) # Assurer que RIB est une chaîne
    
    # 2. Trouver le bénéficiaire correspondant (basé sur le beneficiaire_id_cible)
    beneficiaires_df['ID_Beneficiaire_STR'] = beneficiaires_df['ID_Beneficiaire'].astype(str).str.strip() 
    beneficiaire_data = beneficiaires_df[beneficiaires_df['ID_Beneficiaire_STR'] == beneficiaire_id_cible]

    if beneficiaire_data.empty:
        print(f"❌ Bénéficiaire ID [{beneficiaire_id_cible}] non trouvé dans le fichier bénéficiaires. Saut.")
        return None, current_balance
        
    cheque_data = beneficiaire_data.iloc[0]
    nom_complet_beneficiaire = f"{cheque_data['prenom']} {cheque_data['nom']}"


    # 3. Génération du Montant et Vérification du Solde
    
    # MODIFICATION 1 : Le montant maximum est le solde actuel (current_balance)
    max_amount = max(1.0, current_balance) 
    
    if max_amount < 1.0:
         # Ce cas devrait être géré par la boucle principale, mais une vérification est toujours utile
         print(f"❌ Solde restant insuffisant ({current_balance:.2f} MAD). Ne peut plus émettre de chèques.")
         return None, current_balance
         
    # Génération d'un montant aléatoire entre 1.00 MAD et le solde actuel
    montant_a_payer = round(random.uniform(1.00, max_amount), 2) 

    # La vérification finale est redondante si max_amount est current_balance, 
    # mais assure la robustesse contre les erreurs d'arrondi
    if montant_a_payer > current_balance:
        print(f"❌ Erreur: Montant généré ({montant_a_payer:.2f}) > Solde restant ({current_balance:.2f}). Saut.")
        return None, current_balance

    # --- 4. Préparation et Traitement de la Signature (Inchangé) ---
    signature_path = '' 
    dossier_sign = os.path.join(base_sign_dir, str(client_data['ID_CLIENT_SYNTH'])) 

    if os.path.isdir(dossier_sign):
        images = [f for f in os.listdir(dossier_sign) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if images:
            signature_originale = os.path.join(dossier_sign, images[0])
            signature_transparente_output = os.path.join(
                SIGNATURES_OUTPUT_DIR,
                f"sign_{client_data['ID_CLIENT_SYNTH']}_{images[0].split('.')[0]}.png"
            )
            processed_path = make_signature_transparent(signature_originale, signature_transparente_output)
            
            if processed_path:
                signature_path = f"file:///{os.path.abspath(processed_path)}"
            else:
                print("❌ Échec du traitement de la signature. Le champ restera vide.")
        else:
            print(f"⚠️ Aucune image trouvée pour {client_data['ID_CLIENT_SYNTH']}.")
    else:
        print(f"⚠️ Dossier de signature introuvable: {dossier_sign}")


    # --- 5. Génération des données et de la Ligne MICR ---
    numero_cheque_source = cheque_data['Numero_Cheque']
    date_emission = datetime.now().strftime('%d/%m/%Y')

    # Extraction des composants du RIB 
    if len(client_rib) == 24:
        code_banque = client_rib[0:3]
        code_agent = client_rib[3:6]
        num_compte = client_rib[6:22]
        cle_rib = client_rib[22:24]
    else:
        print(f"❌ RIB du client {client_id} n'a pas 24 chiffres: {client_rib}. MICR omis.")
        code_banque = RIB_BP_PREFIX
        code_agent = "000"
        num_compte = client_rib
        cle_rib = "00"

    # Génération de la ligne MICR
    ligne_micr = generer_ligne_micr(numero_cheque_source, code_banque, code_agent, num_compte, cle_rib)

    # Préparation des données pour le template Jinja
    data_pour_template = {
        'numero_cheque': str(numero_cheque_source).zfill(10), 
        'montant_chiffres': f"{montant_a_payer:.2f}",
        'montant_lettres': convertir_montant_en_lettres(montant_a_payer), 
        'beneficiaire_nom': nom_complet_beneficiaire,
        'client_rib': client_rib, 
        'client_signature_path': signature_path, 
        'ville_emission': VILLE_EMISSION_FIXE, 
        'date_emission': date_emission,
        'client_micr_line': ligne_micr,
    }

    html_rendu = template.render(data_pour_template)
    nom_fichier_png = f"cheque_ID{client_id}_BEN{beneficiaire_id_cible}_M{montant_a_payer:.2f}.png"

    generer_png(html_rendu, nom_fichier_png)
    
    # Déduire le montant du solde et retourner le nouveau solde
    new_balance = current_balance - montant_a_payer
    return montant_a_payer, new_balance


# ----------------------------------------------------------------------
# --- 6. Exécution de la Boucle de Génération (MISE À JOUR) ---
# ----------------------------------------------------------------------

# Préparation initiale des données
base_sign_dir = os.path.abspath("../data/sign_data")

try:
    clients_df = pd.read_csv(CSV_CLIENTS_PATH)
    beneficiaires_df = pd.read_csv(CSV_BENEFICIAIRES_PATH)
except FileNotFoundError as e:
    print(f"Erreur: Fichier de base de données non trouvé. Vérifiez le chemin : {e}")
    exit()

# Nettoyage et filtrage
clients_df['ID_Beneficiaires_Payes'] = clients_df['ID_Beneficiaires_Payes'].astype(str)
clients_df['ID_Beneficiaires_Payes'] = clients_df['ID_Beneficiaires_Payes'].str.replace(r'\.0$', '', regex=True)
clients_df['RIB'] = clients_df['RIB'].astype(str)
bp_clients = clients_df[clients_df['RIB'].str.startswith(RIB_BP_PREFIX)].copy()

if bp_clients.empty:
    print(f"❌ Aucun client trouvé avec un RIB commençant par {RIB_BP_PREFIX}.")
    exit()

# Initialiser un dictionnaire pour suivre le solde de chaque client
client_balances = clients_df.set_index('ID_CLIENT_SYNTH')['Solde_MAD'].to_dict()

# Dictionnaire pour compter les chèques réellement générés
clients_generated_counts = {}

print("\n================ DÉMARRAGE DE LA GÉNÉRATION (1 chèque max par bénéficiaire) ================")

# Mélanger les clients pour varier l'ordre
shuffled_clients = bp_clients.sample(frac=1).reset_index(drop=True)

# Boucle principale : itérer sur chaque client
for index, client_data in shuffled_clients.iterrows():
    client_id = client_data['ID_CLIENT_SYNTH']
    
    # Extraire les IDs uniques des bénéficiaires payables par ce client
    beneficiaire_ids_str = str(client_data['ID_Beneficiaires_Payes']).strip().replace('[', '').replace(']', '').split(',')
    beneficiaire_ids_uniques = [id.strip() for id in beneficiaire_ids_str if id.strip() and id.strip() != 'nan']
    
    if not beneficiaire_ids_uniques:
        print(f"⚠️ Client ID {client_id}: Aucun bénéficiaire valide trouvé.")
        continue
    
    # Sous-boucle : tenter de générer un chèque pour chaque bénéficiaire
    for beneficiaire_id_ref in beneficiaire_ids_uniques:
        current_balance = client_balances.get(client_id, 0.0)
        
        if current_balance < 1.0:
            print(f"❌ Solde insuffisant ({current_balance:.2f} MAD) pour {client_id}. Arrêt des chèques pour ce client.")
            break
            
        montant_emis, new_balance = generer_cheque_client_cible(
            client_data, 
            beneficiaires_df, 
            template, 
            base_sign_dir, 
            SIGNATURES_OUTPUT_DIR, 
            current_balance,
            beneficiaire_id_ref # Le bénéficiaire est maintenant ciblé
        )
        
        if montant_emis is not None:
            # Succès : mettre à jour le solde et le compteur
            clients_generated_counts[client_id] = clients_generated_counts.get(client_id, 0) + 1
            client_balances[client_id] = new_balance
            print(f"    -> {client_id} (vers BEN {beneficiaire_id_ref}): Montant: {montant_emis:.2f} MAD. Solde restant: {new_balance:.2f} MAD.")
            time.sleep(0.5) # Pause légère pour le navigateur
        # Si échec (erreur de données ou solde insuffisant après arrondi), on passe au bénéficiaire suivant
            

print("\n================ FIN DE LA GÉNÉRATION DE CHÈQUES ================ ")
print("Répartition des chèques générés :")
for client_id, count in clients_generated_counts.items():
    if count > 0:
        print(f"Client {client_id}: {count} chèque(s) généré(s). Solde final: {client_balances[client_id]:.2f} MAD.")