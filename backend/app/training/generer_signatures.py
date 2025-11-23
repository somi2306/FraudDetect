# FraudDetect-feature-auth/backend/app/training/generer_signatures.py

import cv2
import numpy as np
import os
import pandas as pd
import kagglehub


def nettoyage_rendu_humain(image_path, output_path, padding=20):
    """
    Nettoie une image de signature en retirant les lignes (utilisant HoughLinesP)
    et en recadrant l'image autour de la signature.
    """
    try:
        stream = open(image_path, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        stream.close()
    except Exception:
        return False

    if img is None:
        return False

    # Transparence
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        bgr = img[:, :, :3]
        bg = np.ones_like(bgr, dtype=np.uint8) * 255
        alpha_factor = alpha[:, :, np.newaxis] / 255.0
        img = (bgr * alpha_factor + bg * (1 - alpha_factor)).astype(np.uint8)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Détection Lignes
    lines = cv2.HoughLinesP(
        thresh,
        rho=1,
        theta=np.pi/180,
        threshold=100,
        minLineLength=img.shape[1] // 3,
        maxLineGap=10
    )

    mask_lines = np.zeros_like(thresh)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))

            if angle < 10 or angle > 80:
                cv2.line(mask_lines, (x1, y1), (x2, y2), 255, 3)

    kernel_repair = np.ones((3, 3), np.uint8)
    mask_signature_safe = cv2.subtract(thresh, mask_lines)
    mask_repaired_full = cv2.morphologyEx(mask_signature_safe, cv2.MORPH_CLOSE, kernel_repair, iterations=1)

    intersection_zone = cv2.bitwise_and(mask_lines, mask_repaired_full)
    patch_zone = cv2.dilate(intersection_zone, np.ones((3, 3), np.uint8), iterations=1)

    final_canvas = np.full_like(gray, 255)
    final_canvas = np.where(mask_signature_safe == 255, gray, final_canvas)

    mask_ink_repair = cv2.bitwise_and(patch_zone, mask_repaired_full)
    final_canvas = np.where(mask_ink_repair == 255, 40, final_canvas)

    contours, _ = cv2.findContours(mask_repaired_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False

    min_x, min_y = img.shape[1], img.shape[0]
    max_x = max_y = 0
    signature_trouvee = False

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 10 or h < 10:
            continue
        if w > img.shape[1] * 0.98:
            continue

        signature_trouvee = True
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    if not signature_trouvee:
        return False

    top = max(0, min_y - padding)
    bottom = min(img.shape[0], max_y + padding)
    left = max(0, min_x - padding)
    right = min(img.shape[1], max_x + padding)

    final_crop = final_canvas[top:bottom, left:right]

    try:
        is_success, im_buf_arr = cv2.imencode(".jpg", final_crop)
        if is_success:
            im_buf_arr.tofile(output_path)
        return True
    except Exception:
        return False


# ==============================
# Lecture Excel depuis /data
# ==============================

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "..", "data")

fichier_source = os.path.join(data_dir, "sign.xlsx")
print("Lecture du fichier de validation :", fichier_source)

validation_map = {}

try:
    df = pd.read_excel(fichier_source)

    for index, row in df.iterrows():
        dossier_id = str(row['Dossier']).strip()
        signatures_valides = []

        for i in range(1, 11):
            col_name = "Signature_" + str(i)
            if col_name in df.columns and pd.notna(row[col_name]):
                nom_image = str(row[col_name]).strip()
                signatures_valides.append(nom_image)

        if signatures_valides:
            validation_map[dossier_id] = signatures_valides

    print(len(validation_map), "dossiers valides")

except Exception as e:
    print("ERREUR lecture fichier :", e)


# ==============================
# Téléchargement Dataset Kaggle
# ==============================

path_dataset = kagglehub.dataset_download("akashgundu/signature-verification-dataset")

output_root = os.path.join(data_dir, "sign_data")

if not os.path.exists(output_root):
    os.makedirs(output_root)

print("Traitement des images vers le répertoire de sortie :", output_root)

compteur_vrai = 0
compteur_faux = 0
compteur_ignore = 0
dossiers_supprimes = 0


for root, dirs, files in os.walk(path_dataset):

    dossier_courant = os.path.basename(root)
    nom_racine = dossier_courant.lower().replace("_forg", "")

    if nom_racine.isdigit():

        dossier_key = str(int(nom_racine))

        if len(validation_map) > 0 and dossier_key not in validation_map:
            if len([f for f in files if f.lower().endswith(('.jpg', '.png', '.jpeg', '.tif'))]) > 0:
                dossiers_supprimes += 1
            continue

        liste_valides = validation_map.get(dossier_key, [])
        est_forg = "_forg" in dossier_courant.lower()

        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg', '.tif')):
                file_path = os.path.join(root, file)

                # 🔥 Correction ici : plus de "extract" ou autres
                nom_final = os.path.basename(root)
                output_dir = os.path.join(output_root, nom_final)

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_file_path = os.path.join(output_dir, file)

                if est_forg:
                    if nettoyage_rendu_humain(file_path, output_file_path):
                        compteur_faux += 1
                        if compteur_faux % 50 == 0:
                            print("[Forg]", compteur_faux, "false traités")

                else:
                    nom_sans_ext = os.path.splitext(file)[0]
                    if len(validation_map) == 0 or nom_sans_ext in liste_valides:
                        if nettoyage_rendu_humain(file_path, output_file_path):
                            compteur_vrai += 1
                            if compteur_vrai % 50 == 0:
                                print("[Vrai]", compteur_vrai, "true traités")
                    else:
                        compteur_ignore += 1


print("\n FIN")
print("true :", compteur_vrai)
print("false :", compteur_faux)
print("Dossiers NV :", dossiers_supprimes, "dossiers")
print("Images NV :", compteur_ignore, "images")
print("Dossier final :", os.path.abspath(output_root))
