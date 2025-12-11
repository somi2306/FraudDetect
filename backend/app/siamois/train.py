import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import numpy as np

# Importer les modules créés
from app.siamois.model import create_base_cnn, create_siamese_model, EMBEDDING_DIM, IMG_HEIGHT, IMG_WIDTH, CHANNELS
from app.siamois.dataset import SiameseTripletGenerator, get_train_test_ids

# --- Hyperparamètres d'Entraînement ---
ROOT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sign_data')
BATCH_SIZE = 32
EPOCHS = 50
MARGIN = 0.5  # La marge alpha (α) pour la Triplet Loss

# --- La fonction de perte Triplet ---
def triplet_loss(y_true, y_pred):
    """
    Calcule la Triplet Loss pour Keras.
    y_pred est une liste de [E_A, E_P, E_N]
    """
    # y_pred est l'output du modèle (la liste des trois embeddings)
    E_A = y_pred[0] # Embedding Ancre
    E_P = y_pred[1] # Embedding Positive
    E_N = y_pred[2] # Embedding Négative
    
    # 1. Calculer la distance Euclidienne au carré
    # La distance au carré est plus simple à dériver et donne le même classement
    def squared_euclidean_distance(x, y):
        sum_square = K.sum(K.square(x - y), axis=1, keepdims=True)
        return sum_square
        
    dist_pos = squared_euclidean_distance(E_A, E_P) # D(A, P)^2
    dist_neg = squared_euclidean_distance(E_A, E_N) # D(A, N)^2
    
    # 2. Calculer la perte : max(0, D(A, P)^2 - D(A, N)^2 + MARGIN)
    loss = K.maximum(dist_pos - dist_neg + MARGIN, 0.0)
    
    return K.mean(loss)

# --- Fonction principale d'Entraînement ---
def train_siamese_network():
    print("--- 1. Préparation des Données ---")
    train_ids, test_ids = get_train_test_ids(ROOT_DATA_DIR, test_ratio=0.2)
    print(f"Identités d'Entraînement: {len(train_ids)}, Identités de Test: {len(test_ids)}")

    train_generator = SiameseTripletGenerator(ROOT_DATA_DIR, train_ids, BATCH_SIZE)
    # Validation Generator peut utiliser les mêmes IDs d'entraînement, ou un sous-ensemble
    val_generator = SiameseTripletGenerator(ROOT_DATA_DIR, train_ids, BATCH_SIZE)

    print(f"Nombre de lots par epoch: {len(train_generator)}")

    print("--- 2. Création et Compilation du Modèle ---")
    input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)
    base_cnn = create_base_cnn(input_shape)
    siamese_model = create_siamese_model(base_cnn)

    # Compilation: la Triplet Loss est appliquée à la sortie du modèle
    siamese_model.compile(loss=triplet_loss, optimizer=Adam(learning_rate=1e-4))

    # --- 3. Callbacks et Entraînement ---
    model_save_path = os.path.join(os.path.dirname(__file__), 'siamese_best_model.h5')
    
    callbacks = [
        ModelCheckpoint(model_save_path, monitor='loss', save_best_only=True, verbose=1),
        EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
    ]
    
    print("--- Démarrage de l'Entraînement ---")
    siamese_model.fit(
        train_generator,
        steps_per_epoch=len(train_generator),
        epochs=EPOCHS,
        callbacks=callbacks,
        validation_data=val_generator,
        validation_steps=len(val_generator) // 5, # Utilise 1/5 des steps pour la validation
        verbose=1
    )
    
    print("\nEntraînement terminé. Meilleur modèle sauvegardé à :", model_save_path)

if __name__ == '__main__':
    train_siamese_network()