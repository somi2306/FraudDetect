import pandas as pd
import random
import os
from num2words import num2words
from datetime import datetime, timedelta

print("Script de génération des transactions de chèques démarré...")

# --- 1. CONFIGURATION DES CHEMINS ---
PATH_CLIENTS = "backend/app/data/clients_training_map.csv"
PATH_BENEFICIAIRES = "backend/app/data/beneficiaires.csv"
PATH_TRANSACTIONS_OUT = "backend/app/data/transactions_cheques.csv"

# --- 2. CHARGEMENT DES DONNÉES DE BASE ---
try:
    df_clients = pd.read_csv(PATH_CLIENTS)
    df_beneficiaires = pd.read_csv(PATH_BENEFICIAIRES)
except FileNotFoundError as e:
    print(f"ERREUR FATALE: Fichier non trouvé. {e}")
    exit()

print(f"✅ Fichiers chargés : {len(df_clients)} clients et {len(df_beneficiaires)} bénéficiaires.")

# --- 3. GÉNÉRATION DES TRANSACTIONS ---
transactions = []
villes_marocaines = ["Tanger", "Casablanca", "Rabat", "Marrakech", "Fès", "Agadir"]

# ✅ NOUVEAU : Dictionnaire des agences CIH (basé sur la recherche)
AGENCES_CIH_MAP = {
    "Tanger": {"adresse": "49 Av. Anfa, Souani, Tanger", "tel": "0539 93 11 25"},
    "Casablanca": {"adresse": "128, Avenue 2 mars, Casablanca", "tel": "0522 85 92 80"},
    "Rabat": {"adresse": "Rue Abd. El Ghafiqui, Agdal, Rabat", "tel": "0537 68 56 90"},
    "Marrakech": {"adresse": "187, Av. Mohammed V, Gueliz", "tel": "0524 43 03 20"},
    "Fès": {"adresse": "LOT 3, Rte Immouzer, Fes-Saiss", "tel": "0535 64 41 22"},
    "Agadir": {"adresse": "Bd Mohammed V, Cplxe Fdn Hassan II", "tel": "0528 84 17 97"}
}

cheque_counter = 1000001 # Numéro de chèque unique pour l'émetteur

for _, client in df_clients.iterrows():
    
    # Convertir la liste string "[1, 401]" en vraie liste [1, 401]
    try:
        beneficiaire_ids = eval(client['ID_Beneficiaires_Payes'])
    except Exception:
        continue

    # 1. Simuler un montant pour chaque bénéficiaire
    montants = []
    for _ in beneficiaire_ids:
        # Montant de base entre 100 et 10,000 DH
        montants.append(round(random.uniform(100, 10000), 2))

    # 2. Simuler la FRAUDE DE SOLDE (Niveau 2)
    # 15% de chance que le client tente de payer plus que ce qu'il n'a
    is_fraude_solde = False
    if random.uniform(0, 1) < 0.15: 
        # Le client paie 1.5x son solde (fraude)
        total_a_payer = client['Solde_MAD'] * 1.5
        # Répartir ce montant frauduleux
        montants = [round(total_a_payer / len(montants), 2)] * len(montants)
        is_fraude_solde = True

    # 3. Créer une transaction pour chaque chèque
    for i, benef_id in enumerate(beneficiaire_ids):
        
        montant_actuel = montants[i]
        
        # 4. Simuler la FRAUDE DE MONTANT (Niveau 1)
        # 10% de chance que les lettres et les chiffres ne correspondent pas
        is_fraude_montant = False
        montant_lettres = num2words(montant_actuel, lang='fr').replace(" virgule ", " et ") + " dirhams"
        
        if random.uniform(0, 1) < 0.10:
            is_fraude_montant = True
            # Le texte est pour 1000 DH, mais les chiffres montrent autre chose
            montant_lettres = "Mille dirhams" 

        # 5. Récupérer les infos
        benef_info = df_beneficiaires[df_beneficiaires['ID_Beneficiaire'] == benef_id].iloc[0]
        client_rib = str(client['RIB']).zfill(24)
        
        # ✅ MODIFIÉ : Choisir le lieu et l'agence AVANT de créer la transaction
        lieu_emission = random.choice(villes_marocaines)
        agence_info = AGENCES_CIH_MAP[lieu_emission]

        transactions.append({
            "ID_Transaction": len(transactions) + 1,
            "ID_CLIENT_SYNTH": client['ID_CLIENT_SYNTH'],
            "ID_Beneficiaire": benef_id,
            "Nom_Beneficiaire": f"{benef_info['prenom']} {benef_info['nom']}",
            
            # Données du Chèque
            "Montant_Chiffres": montant_actuel,
            "Montant_Lettres": montant_lettres,
            "Lieu_Emission": lieu_emission,
            "Date_Emission": (datetime.now() - timedelta(days=random.randint(5, 365))).strftime("%d-%m-%Y"),
            "Numero_Cheque_Emetteur": cheque_counter,
            
            # ✅ NOUVEAU : Données de l'agence (déjà présentes dans votre fichier)
            "Agence_Adresse": agence_info["adresse"],
            "Agence_Telephone": agence_info["tel"],
            
            # Données Client (pour le chèque)
            "Nom_Emetteur": f"{client['Prénom']} {client['Nom']}",
            "Code_Banque": client_rib[0:3],
            
            # ✅ CORRIGÉ : Assure 5 chiffres pour Agent et 14 pour Compte
            "Code_Agent": client_rib[3:6],
            "Numero_Compte": client_rib[6:22],
            "Cle_RIB": client_rib[22:24],
            "Signature_Path_Genuine": client['PATH_GENUINE'], # Pour la vraie signature
            
            # Statuts de Fraude (pour l'entraînement)
            "is_Fraude_Solde": is_fraude_solde, # Fraude Comportementale
            "is_Fraude_Montant": is_fraude_montant # Fraude Visuelle (CAR/LAR)
        })
        cheque_counter += 1

# --- 4. SAUVEGARDE ---
df_transactions = pd.DataFrame(transactions)
df_transactions.to_csv(PATH_TRANSACTIONS_OUT, index=False, encoding='utf-8')

print(f"\n✅ {len(df_transactions)} transactions de chèques générées.")
print(f"💾 Fichier sauvegardé dans : {PATH_TRANSACTIONS_OUT}")
print("\nExemple de structure des transactions (avec nouvelles colonnes) :")
print(df_transactions[['ID_Transaction', 'Lieu_Emission', 'Agence_Adresse', 'Agence_Telephone']].head())