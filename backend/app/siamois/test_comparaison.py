import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os

# ============================================================
# IMPORTS LOCAUX (fonctions créées dans les autres fichiers)
# ============================================================
# preprocess_image : prépare une image (taille, normalisation…)
from .dataset import preprocess_image

# triplet_loss : fonction de perte utilisée à l'entraînement
# (obligatoire pour recharger le modèle)
from .train import triplet_loss

# normalize_embedding : normalisation du vecteur de signature
# (également nécessaire au chargement du modèle)
from .model import normalize_embedding


# ============================================================
# 1) CONFIGURATION GÉNÉRALE
# ============================================================
# Chemin vers le modèle entraîné (sauvegardé précédemment)
# Il est situé dans le même dossier que ce script
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'siamese_best_model.h5')

# Seuil de décision :
# - si la distance entre deux signatures est INFÉRIEURE à ce seuil
#   → signatures considérées comme similaires
# - sinon → signatures différentes
SEUIL_DE_DECISION = 0.5


# ============================================================
# 2) FONCTION DE COMPARAISON DE DEUX SIGNATURES
# ============================================================
def compare_two_signatures(path_img1, path_img2):
    """
    Compare deux images de signatures et affiche le résultat.

    Entrées :
    - path_img1 : chemin vers la première image
    - path_img2 : chemin vers la deuxième image

    Sortie :
    - Affichage de la distance calculée
    - Verdict : signatures similaires ou différentes
    """

    # --------------------------------------------------------
    # 1) Charger le modèle entraîné
    # --------------------------------------------------------
    try:
        # Vérifier que le fichier du modèle existe
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Erreur : Le fichier du modèle n'existe pas à l'emplacement : {MODEL_PATH}")
            return

        # Charger le modèle complet (réseau siamois)
        # custom_objects est obligatoire car :
        # - triplet_loss
        # - normalize_embedding
        # ne font pas partie de TensorFlow par défaut
        full_model = load_model(
            MODEL_PATH,
            custom_objects={
                'triplet_loss': triplet_loss,
                'normalize_embedding': normalize_embedding
            }
        )

        # ----------------------------------------------------
        # Extraire uniquement le modèle d'embedding (Base_CNN)
        # ----------------------------------------------------
        # On ne veut PAS comparer des triplets ici,
        # mais seulement transformer une image en vecteur.
        embedding_model = tf.keras.Model(
            inputs=full_model.get_layer('Base_CNN').input,
            outputs=full_model.get_layer('Base_CNN').output
        )

        print("✅ Modèle chargé avec succès.")

    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")
        return

    # --------------------------------------------------------
    # 2) Prétraiter les deux images
    # --------------------------------------------------------
    try:
        # Charger + redimensionner + normaliser les images
        img1 = preprocess_image(path_img1)
        img2 = preprocess_image(path_img2)

    except Exception as e:
        print(f"❌ Erreur lecture images : {e}")
        return

    # Ajouter la dimension "batch"
    # Le modèle attend une entrée de forme :
    # (nombre_d_images, hauteur, largeur, canaux)
    img1 = np.expand_dims(img1, axis=0)
    img2 = np.expand_dims(img2, axis=0)

    # --------------------------------------------------------
    # 3) Générer les embeddings (vecteurs numériques)
    # --------------------------------------------------------
    # Chaque signature est transformée en un vecteur de 512 valeurs
    emb1 = embedding_model.predict(img1)
    emb2 = embedding_model.predict(img2)

    # --------------------------------------------------------
    # 4) Calculer la distance entre les deux signatures
    # --------------------------------------------------------
    # Distance euclidienne au carré :
    # - petite distance  → signatures proches (similaires)
    # - grande distance → signatures éloignées (différentes)
    distance = np.sum(np.square(emb1 - emb2))

    # --------------------------------------------------------
    # 5) Affichage du résultat
    # --------------------------------------------------------
    print("\n" + "=" * 40)
    print(f"Image 1 : {os.path.basename(path_img1)}")
    print(f"Image 2 : {os.path.basename(path_img2)}")
    print(f"DISTANCE calculée : {distance:.4f}")

    if distance < SEUIL_DE_DECISION:
        print(f"RÉSULTAT : ✅ SIGNATURES SIMILAIRES (< {SEUIL_DE_DECISION})")
    else:
        print(f"RÉSULTAT : ❌ SIGNATURES DIFFÉRENTES (> {SEUIL_DE_DECISION})")

    print("=" * 40)


# ============================================================
# 3) BLOC PRINCIPAL (exécution directe du script)
# ============================================================
if __name__ == "__main__":
    # Exemples de chemins vers deux signatures à comparer
    # (à adapter selon votre organisation de fichiers)
    img_A = "app/data/sign_data/001/1-001_01.jpg"
    img_B = "app/data/sign_data/001_forg/1-002_01.jpg"

    print("Lancement du test de comparaison...")
    compare_two_signatures(img_A, img_B)
