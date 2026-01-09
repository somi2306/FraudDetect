from playwright.sync_api import sync_playwright
import pandas as pd
from jinja2 import Template
import os
import ast
from num2words import num2words
from datetime import datetime
import random
from PIL import Image

villes = [
    "Rabat", "Casablanca", "Marrakech", "Fès", "Tanger",
    "Agadir", "Oujda", "Meknès", "Laâyoune", "Kenitra"
]


from num2words import num2words

def montant_en_lettres(montant):
    """
    Convertit un montant en lettres au format utilisé dans les chèques marocains.
    Exemple : 123.45 → 'cent vingt-trois dirhams et quarante-cinq centimes'
    """
    # Séparer partie entière et centimes
    partie_entiere = int(montant)
    centimes = int(round((montant - partie_entiere) * 100))

    # Convertir partie entière
    if partie_entiere == 0:
        lettres_entiere = "zéro dirham"
    elif partie_entiere == 1:
        lettres_entiere = "un dirham"
    else:
        lettres_entiere = num2words(partie_entiere, lang='fr') + " dirhams"

    # Convertir centimes
    if centimes == 0:
        return lettres_entiere + " et zéro centime"

    elif centimes == 1:
        lettres_centimes = "un centime"
    else:
        lettres_centimes = num2words(centimes, lang='fr') + " centimes"

    return lettres_entiere + " et " + lettres_centimes

# === Fonction pour rendre le fond de la signature transparent ===
def make_signature_transparent(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        r, g, b, a = item
        if r > 240 and g > 240 and b > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append((0, 0, 0, 255))

    img.putdata(newData)
    img.save(output_path, "PNG")
    return output_path

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
        
        # Le code banque (3) et le code agent (3) sont regroupés pour le "Transit" selon le format RIB marocain
        transit_str = f"{str(code_banque).zfill(3)}{str(code_agent).zfill(3)}" 
        
        # Le numéro de compte (16) et la clé RIB (2) sont combinés pour le "On Us"
        compte_part = str(num_compte).zfill(16)
        cle_part = str(cle_rib).zfill(2)
        compte_cle_str = f"{compte_part}{ON_US}{cle_part}" # Note: ON_US est inséré entre compte et clé

        # Formatage final: chèque_num / banque+guichet / num_compte+cle_rib
        return f"{TRANSIT}{cheque_str}{TRANSIT} {transit_str} {ON_US}{compte_cle_str}{ON_US}"
        
    except Exception as e:
        print(f"!!! Erreur lors de la génération MICR: {e}")
        return ""

# ---
# === Créer dossier de sortie ===
os.makedirs("../data/chequesTIJARI/", exist_ok=True)
os.makedirs("../data/cheques/TIJARI/signatures_transparentes", exist_ok=True)

# === Charger les données ===
clients = pd.read_csv("../data/clients_training_map.csv")
beneficiaries = pd.read_csv("../data/beneficiaires.csv")
# Assurez-vous que la colonne RIB est traitée comme une chaîne de caractères
clients["RIB_str"] = clients["RIB"].astype(str).str.zfill(24) 
clients_filtrés = clients[clients["RIB_str"].str.startswith("007")]

if clients_filtrés.empty:
    print("⚠️ Aucun client avec un RIB commençant par '007'.")
else:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for _, client in clients_filtrés.iterrows():
            try:
                ben_ids = ast.literal_eval(client["ID_Beneficiaires_Payes"])
            except Exception as e:
                print(f"⚠️ Erreur parsing ID_Beneficiaires_Payes pour {client['Nom']} : {e}")
                ben_ids = []

            if not ben_ids:
                continue

            # === Extraire les composants du RIB ===
            rib_complet = client["RIB_str"]
            code_banque = rib_complet[0:3]
            code_agent = rib_complet[3:6]
            num_compte = rib_complet[6:22]
            cle_rib = rib_complet[22:24]
            # ---

            solde_restant = client["Solde_MAD"]

            # === Préparer la signature (code inchangé) ===
            signature_path = None
            base_sign_dir = os.path.abspath("../data/sign_data")
            dossier_sign = os.path.join(base_sign_dir, str(client["ID_CLIENT_SYNTH"]))

            if os.path.isdir(dossier_sign):
                images = [f for f in os.listdir(dossier_sign) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
                if images:
                    signature_originale = os.path.join(dossier_sign, images[0])
                    signature_transparente_path = os.path.join(
                        "../data/cheques/TIJARI/signatures_transparentes",
                        f"{client['ID_CLIENT_SYNTH']}_{images[0].split('.')[0]}.png"
                    )
                    make_signature_transparent(signature_originale, signature_transparente_path)
                    signature_path = os.path.abspath(signature_transparente_path)
                else:
                    print(f"⚠️ Aucune image trouvée pour {client['Nom']} dans {dossier_sign}")
            else:
                print(f"⚠️ Dossier introuvable: {dossier_sign}")
            # ---

            # === Générer un chèque par bénéficiaire ===
            for ben_id in ben_ids:
                ben = beneficiaries.loc[beneficiaries["ID_Beneficiaire"] == ben_id]
                if ben.empty or solde_restant <= 0:
                    continue
                ben = ben.iloc[0]
                lieu_aleatoire = random.choice(villes)
                montant = round(random.uniform(1, solde_restant), 2)
                montant_lettres = montant_en_lettres(montant)
                
                # === Générer la ligne MICR ===
                ligne_micr = generer_ligne_micr(
                    cheque_num=ben["Numero_Cheque"], # Le numéro de chèque vient du bénéficiaire
                    code_banque=code_banque,
                    code_agent=code_agent,
                    num_compte=num_compte,
                    cle_rib=cle_rib
                )
                # ---

                # === Lire le template HTML ===
                with open("../data/cheques_templates/TIJARI Cheque/cheque.html", "r", encoding="utf-8") as f:
                    template_html = f.read()
                template = Template(template_html)

                html_content = template.render(
                    rib=client["RIB_str"],
                    beneficiaire_nom=ben["nom"],
                    beneficiaire_prenom=ben["prenom"],
                    numero_cheque=ben["Numero_Cheque"],
                    montant=montant,
                    lieu=lieu_aleatoire,  
                    montant_lettres=montant_lettres,
                    date=datetime.today().strftime("%d/%m/%Y"),
                    signature=signature_path,
                    ligne_micr=ligne_micr # AJOUT de la ligne MICR
                )

                # === Remplacer le placeholder de la signature (code inchangé) ===
                if signature_path:
                    signature_url = f"file:///{signature_path.replace(os.sep, '/')}"
                    html_content = html_content.replace("PLACEHOLDER_SIGNATURE_IMG", signature_url)
                else:
                    html_content = html_content.replace("PLACEHOLDER_SIGNATURE_IMG", "")
                # ---

                # === Sauvegarder temporairement le HTML (code inchangé) ===
                html_file = f"../data/cheques/TIJARI/temp_{client['ID_CLIENT_SYNTH']}_{ben['Numero_Cheque']}.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                # ---

                # === Charger HTML avec Playwright et prendre screenshot (code inchangé) ===
                page.goto(f"file:///{os.path.abspath(html_file)}")
                
                output_file = f"../data/cheques/TIJARI/cheque_{client['ID_CLIENT_SYNTH']}_{ben['Numero_Cheque']}.png"
                page.set_viewport_size({"width": 833, "height": 429})
                page.screenshot(path=output_file, full_page=True)
                

                print(f"✅ Chèque généré pour {ben['prenom']} {ben['nom']} ({client['Nom']}): {output_file}")

                solde_restant -= montant

        browser.close()