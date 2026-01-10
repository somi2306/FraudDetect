import tensorflow as tf
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.model_selection import train_test_split  # Pour découper les IDs en train/validation
import os
import numpy as np
import tensorflow.keras.backend as K

# ============================================================
# Importer les modules du projet (réseau + dataset)
# ============================================================
# - create_base_cnn : construit le "réseau de base" qui transforme une image en vecteur (embedding)
# - create_siamese_model : construit le modèle final qui travaille avec 3 images (Anchor/Positive/Negative)
# - EMBEDDING_DIM : taille du vecteur de sortie (ex: 512)
# - IMG_HEIGHT / IMG_WIDTH / CHANNELS : dimensions d'entrée des images
from .model import create_base_cnn, create_siamese_model, EMBEDDING_DIM, IMG_HEIGHT, IMG_WIDTH, CHANNELS

# - SiameseTripletGenerator : génère des lots (batches) d'images en triplets (A, P, N)
# - get_train_test_ids : sépare les identités en train et test
from .dataset import SiameseTripletGenerator, get_train_test_ids

# ============================================================
# 1) HYPERPARAMÈTRES D'ENTRAÎNEMENT (réglages)
# ============================================================
# Chemin du dossier contenant les données (signatures)
ROOT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sign_data')

# Taille d'un batch :
# Exemple : 32 => on entraîne sur 32 triplets à chaque itération
BATCH_SIZE = 32

# Nombre maximum de "tours d'entraînement" (epochs)
EPOCHS = 50

# MARGIN : la marge (alpha) utilisée par la Triplet Loss
# Intuition : on veut que la distance (Anchor vs Négatif) soit AU MOINS
# plus grande que (Anchor vs Positif) d'une valeur "MARGIN".
MARGIN = 0.5

# ============================================================
# 2) FONCTION DE PERTE : Triplet Loss
# ============================================================
# Cette fonction indique au modèle ce qu'il doit "optimiser".
#
# On a 3 vecteurs (embeddings) :
# - anchor   : représentation de la signature authentique A
# - positive : représentation d'une autre authentique P (même personne)
# - negative : représentation d'une falsifiée N (contrefaçon)
#
# Objectif :
# - rapprocher anchor et positive
# - éloigner anchor et negative
def triplet_loss(y_true, y_pred):
    # y_pred contient en réalité une concaténation de 3 embeddings :
    # [ anchor_embedding | positive_embedding | negative_embedding ]
    #
    # Donc on découpe y_pred en 3 morceaux, chacun de taille EMBEDDING_DIM.

    anchor = y_pred[:, 0:EMBEDDING_DIM]
    positive = y_pred[:, EMBEDDING_DIM:2*EMBEDDING_DIM]
    negative = y_pred[:, 2*EMBEDDING_DIM:3*EMBEDDING_DIM]

    # Calcul des distances (distance euclidienne au carré)
    # - pos_dist : distance entre A et P (on veut qu'elle soit petite)
    # - neg_dist : distance entre A et N (on veut qu'elle soit grande)
    pos_dist = K.sum(K.square(anchor - positive), axis=-1)
    neg_dist = K.sum(K.square(anchor - negative), axis=-1)

    # Formule de la Triplet Loss :
    # loss = max( pos_dist - neg_dist + MARGIN , 0 )
    #
    # Si neg_dist est déjà suffisamment plus grande que pos_dist (grâce à la marge),
    # la perte devient 0 => le modèle "a bien fait" pour ce triplet.
    loss = K.maximum(pos_dist - neg_dist + MARGIN, 0.0)

    # On renvoie la moyenne sur le batch (une seule valeur)
    return K.mean(loss)


# ============================================================
# 3) FONCTION PRINCIPALE : entraînement du réseau
# ============================================================
def train_siamese_network():
    print("--- 1. Préparation des Données ---")

    # 1) Séparer toutes les identités en :
    # - train_val : utilisé pour entraîner + valider
    # - final_test : gardé à part pour un test final "honnête" (non vu pendant l'entraînement)
    all_train_val_ids, final_test_ids = get_train_test_ids(ROOT_DATA_DIR, test_ratio=0.2)

    print(
        f"Identités à entraîner/valider: {len(all_train_val_ids)}, "
        f"Identités de Test Final (réservé): {len(final_test_ids)}"
    )

    # 2) À l'intérieur du "train_val", on crée :
    # - train_ids : identités réellement utilisées pour apprendre
    # - val_ids   : identités utilisées pour vérifier si le modèle généralise bien
    #
    # test_size=0.15 => 15% des IDs de train_val seront pour validation
    # random_state=42 => fixe le hasard pour avoir le même split à chaque exécution
    train_ids, val_ids = train_test_split(
        all_train_val_ids,
        test_size=0.15,
        random_state=42
    )

    print(f"Identités d'Entraînement (réel): {len(train_ids)}, Identités de Validation: {len(val_ids)}")

    # 3) Création des générateurs (ce sont des "robots" qui fabriquent des triplets en continu)
    # train_generator produit des triplets pour l'entraînement
    train_generator = SiameseTripletGenerator(ROOT_DATA_DIR, train_ids, BATCH_SIZE)

    # val_generator produit des triplets pour la validation
    # (IMPORTANT : il utilise les IDs de validation, pas ceux du train)
    val_generator = SiameseTripletGenerator(ROOT_DATA_DIR, val_ids, BATCH_SIZE)

    print(f"Nombre de lots par epoch: {len(train_generator)}")

    print("--- 2. Création et Compilation du Modèle ---")

    # Définir la forme des images attendues par le modèle (hauteur, largeur, canaux)
    input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)

    # base_cnn : le réseau qui transforme UNE image en embedding (vecteur)
    base_cnn = create_base_cnn(input_shape)

    # siamese_model : modèle complet qui reçoit 3 images (A, P, N)
    # et renvoie les 3 embeddings (souvent concaténés)
    siamese_model = create_siamese_model(base_cnn)

    # Compilation :
    # - loss=triplet_loss : la fonction qui guide l'apprentissage
    # - optimizer=Adam : l'algorithme qui met à jour les poids du réseau
    # learning_rate=1e-4 => vitesse d'apprentissage (petite pour être stable)
    siamese_model.compile(loss=triplet_loss, optimizer=Adam(learning_rate=1e-4))

    # ============================================================
    # 4) CALLBACKS : "outils automatiques" pendant l'entraînement
    # ============================================================
    model_save_path = os.path.join(os.path.dirname(__file__), 'siamese_best_model.h5')

    callbacks = [
        # ModelCheckpoint :
        # Sauvegarde automatiquement le meilleur modèle (celui qui a la plus faible val_loss)
        ModelCheckpoint(model_save_path, monitor='val_loss', save_best_only=True, verbose=1),

        # EarlyStopping :
        # Arrête l'entraînement si la val_loss n'améliore plus après un certain temps
        # patience=10 => on attend 10 epochs sans amélioration avant d'arrêter
        # restore_best_weights=True => on récupère automatiquement les meilleurs poids
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    ]

    print("--- Démarrage de l'Entraînement ---")

    # Lancement de l'entraînement
    siamese_model.fit(
        train_generator,
        steps_per_epoch=len(train_generator),   # combien de batches par epoch
        epochs=EPOCHS,
        callbacks=callbacks,
        validation_data=val_generator,
        validation_steps=len(val_generator),    # combien de batches de validation
        verbose=1
    )

    print("\nEntraînement terminé. Meilleur modèle sauvegardé à :", model_save_path)


# ============================================================
# 5) Exécution directe du script
# ============================================================
# Si on lance ce fichier directement (python train.py),
# alors on démarre l'entraînement.
if __name__ == '__main__':
    train_siamese_network()
