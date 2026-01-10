import os
import random
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.utils import Sequence
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from .model import EMBEDDING_DIM

# ============================================================
# 1) PARAMÈTRES GÉNÉRAUX (taille et format des images)
# ============================================================
# Pour entraîner un réseau de neurones, toutes les images d’entrée
# doivent avoir la même taille. Ici on impose :
IMG_HEIGHT = 100
IMG_WIDTH = 200

# Nombre de canaux (couleurs) :
# - 3 canaux => image couleur (RGB)
# - 1 canal  => image en niveaux de gris (noir et blanc)
CHANNELS = 1  # Niveaux de Gris

# ------------------------------------------------------------
# Les images seront lues depuis un dossier "train" (ou un dossier
# racine), qui contient des sous-dossiers par signataire.
# ------------------------------------------------------------


def preprocess_image(path):
    """
    Objectif :
    - Ouvrir une image (signature)
    - La rendre compatible avec le modèle (même taille pour toutes)
    - Garder le ratio (ne pas étirer la signature)
    - Ajouter du "padding" (bordures noires) si nécessaire
    - Normaliser les valeurs (pixels entre 0 et 1)

    Entrée : chemin vers une image (path)
    Sortie : un tableau numpy de forme (100, 200, 1) avec valeurs [0..1]
    """

    # 1) Ouvrir l’image et la convertir en niveaux de gris
    # convert('L') => mode grayscale (un seul canal)
    img = Image.open(path).convert('L')

    # On récupère la taille originale de l’image (largeur, hauteur)
    original_w, original_h = img.size

    # Taille cible (ce que le réseau attend)
    target_h, target_w = IMG_HEIGHT, IMG_WIDTH

    # 2) Calculer le ratio de redimensionnement
    # On veut que l’image "rentre" dans (200x100) sans déformation.
    # Donc on prend le ratio le plus petit : soit basé sur la largeur,
    # soit basé sur la hauteur.
    ratio = min(target_w / original_w, target_h / original_h)

    # Nouvelles dimensions après redimensionnement (en gardant le ratio)
    new_w = int(original_w * ratio)
    new_h = int(original_h * ratio)

    # 3) Redimensionner l’image avec un filtre de bonne qualité
    # LANCZOS est un mode de redimensionnement souvent utilisé car il
    # donne un résultat plus propre (moins pixelisé).
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 4) Créer une image vide (canevas) de taille fixe en noir
    # Image.new('L', (largeur, hauteur), 0) :
    # - 'L' => grayscale
    # - 0  => noir
    new_img = Image.new('L', (target_w, target_h), 0)

    # 5) Calculer où coller l’image pour la centrer
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2

    # On colle l’image redimensionnée au centre du canevas noir
    new_img.paste(img, (x_offset, y_offset))

    # 6) Convertir en tableau numpy et normaliser
    # Le modèle ne travaille pas directement avec "Image PIL", il faut
    # un tableau de nombres.
    img_array = np.array(new_img, dtype=np.float32)

    # Ajouter la dimension du canal pour avoir (hauteur, largeur, 1)
    img_array = np.expand_dims(img_array, axis=-1)

    # Normaliser les pixels : au lieu d’être entre 0..255,
    # ils deviennent entre 0..1 (meilleur pour l’apprentissage).
    img_array = img_array / 255.0

    return img_array


# ============================================================
# 2) GÉNÉRATION DE TRIPLETS POUR UN RÉSEAU SIAMOIS (Triplet Loss)
# ============================================================
# Un réseau "siamois" apprend à comparer des images.
# Avec la Triplet Loss, on fournit au modèle des groupes de 3 images :
#   A = Anchor   : une signature authentique de la personne
#   P = Positive : une autre signature authentique de la même personne
#   N = Negative : une signature falsifiée (contrefaçon) de cette personne
#
# Le but :
# - rapprocher A et P dans l’espace d’embedding
# - éloigner A et N
#
# Cette classe génère automatiquement des lots (batches) de triplets
# pendant l’entraînement.
class SiameseTripletGenerator(Sequence):
    def __init__(self, root_dir, signataire_ids, batch_size):
        # root_dir : dossier racine contenant les images organisées par dossiers
        # signataire_ids : liste des IDs (personnes) à utiliser
        # batch_size : nombre de triplets par batch
        self.root_dir = root_dir
        self.signataire_ids = signataire_ids
        self.batch_size = batch_size

        # On prépare une structure interne qui stocke :
        # pour chaque personne => la liste des images authentiques et falsifiées
        self.identities = self._collect_identities()

        # Nombre de batches par epoch (valeur "fixe" choisie ici)
        # Cela signifie : dans une epoch, on va générer 1000 batches.
        self.steps_per_epoch = 1000  # Un nombre arbitraire élevé de triplets par epoch

    def _collect_identities(self):
        """
        Rôle :
        - Parcourir les dossiers des signataires
        - Construire une structure du type :
            {
              "001": {"auth": [...], "forg": [...]},
              "002": {"auth": [...], "forg": [...]},
              ...
            }

        Convention supposée :
        - Authentiques : root_dir/<id>/
        - Falsifiées   : root_dir/<id>_forg/
        """
        identities_data = {}

        for id in self.signataire_ids:
            # Dossier signatures authentiques
            auth_dir = os.path.join(self.root_dir, id)

            # Dossier signatures falsifiées (contrefaçons)
            forg_dir = os.path.join(self.root_dir, id + '_forg')

            # On liste les fichiers images dans chaque dossier
            # (on ne garde que .png et .jpg)
            auth_files = [
                os.path.join(auth_dir, f)
                for f in os.listdir(auth_dir)
                if f.endswith(('.png', '.jpg'))
            ]
            forg_files = [
                os.path.join(forg_dir, f)
                for f in os.listdir(forg_dir)
                if f.endswith(('.png', '.jpg'))
            ]

            # Pour créer un triplet, il faut :
            # - au moins 2 authentiques (A et P)
            # - au moins 1 falsifiée (N)
            if len(auth_files) >= 2 and len(forg_files) >= 1:
                identities_data[id] = {'auth': auth_files, 'forg': forg_files}

        # Si aucune identité n’est valide, on stoppe avec une erreur explicite
        if not identities_data:
            raise ValueError("Aucune identité valide trouvée avec assez d'images pour créer des triplets.")

        print(f"Dataset initialisé avec {len(identities_data)} signataires valides.")
        return identities_data

    def __len__(self):
        """
        Keras demande : combien de batches dans une epoch ?
        Ici, on renvoie la valeur définie dans steps_per_epoch.
        """
        return self.steps_per_epoch

    def __getitem__(self, index):
        """
        Génère 1 batch (lot) de triplets.

        Sortie attendue par Keras :
        - inputs  : (A_batch, P_batch, N_batch)
        - outputs : ici on met des "dummy" (faux labels), car la Triplet Loss
                   ne nécessite pas des labels classiques (0/1).
        """

        # On crée des tableaux vides pour stocker les images du batch
        # Forme : (batch_size, hauteur, largeur, channels)
        A_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))
        P_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))
        N_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))

        # Triplet Loss : on n’a pas vraiment besoin de y_true (étiquette)
        # Mais Keras attend quand même quelque chose.
        # On renvoie donc un tableau "dummy" (rempli de zéros).
        dummy_y = np.zeros((self.batch_size, EMBEDDING_DIM))

        # Liste des identités disponibles
        identity_ids = list(self.identities.keys())

        for i in range(self.batch_size):
            # 1) Choisir une identité aléatoire (une personne)
            anchor_id = random.choice(identity_ids)
            id_data = self.identities[anchor_id]

            # 2) Choisir 2 signatures authentiques différentes pour A et P
            anchor_path, positive_path = random.sample(id_data['auth'], 2)

            # 3) Choisir 1 signature falsifiée pour N
            negative_path = random.choice(id_data['forg'])

            # 4) Charger et prétraiter chaque image (même taille + normalisation)
            A_batch[i] = preprocess_image(anchor_path)
            P_batch[i] = preprocess_image(positive_path)
            N_batch[i] = preprocess_image(negative_path)

        # Keras/TensorFlow attend : (inputs), (outputs)
        # Ici, outputs est répété 3 fois (selon la structure du modèle Siamois).
        return (A_batch, P_batch, N_batch), (dummy_y, dummy_y, dummy_y)


# ============================================================
# 3) SÉPARATION TRAIN / TEST DES IDENTIFIANTS (IDs)
# ============================================================
def get_train_test_ids(root_dir, test_ratio=0.2):
    """
    Rôle :
    - Récupérer tous les IDs (signataires) dans le dossier racine
    - Les mélanger au hasard
    - Les séparer en :
        * train_ids : pour entraîner le modèle
        * test_ids  : pour tester / évaluer le modèle

    test_ratio=0.2 => 20% des IDs en test, 80% en train
    """

    # Lister tous les sous-dossiers dans root_dir
    all_dirs = [
        d for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d))
    ]

    # Certains dossiers ont la forme "001" et "001_forg"
    # On veut récupérer les IDs uniques sans le suffixe "_forg"
    unique_ids = sorted(list(set([d.split('_')[0] for d in all_dirs])))

    # Mélanger aléatoirement pour éviter que la séparation soit biaisée
    random.shuffle(unique_ids)

    # Calculer combien vont aller en test
    test_size = int(len(unique_ids) * test_ratio)

    # Découper la liste :
    # - test = les premiers
    # - train = le reste
    train_ids = unique_ids[test_size:]
    test_ids = unique_ids[:test_size]

    return train_ids, test_ids
