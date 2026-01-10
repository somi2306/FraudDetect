import os
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
import tensorflow.keras.backend as K

# Imports locaux sécurisés
from .dataset import get_train_test_ids, preprocess_image, SiameseTripletGenerator
from .train import triplet_loss
from .model import (
    IMG_HEIGHT, 
    IMG_WIDTH, 
    CHANNELS, 
    EMBEDDING_DIM, 
    normalize_embedding
)

# --- Configuration ---
ROOT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sign_data')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'siamese_best_model.h5')
SEUIL_DE_DECISION = 0.5  # Seuil initial pour D(A, B)^2
NUM_TEST_PAIRS = 1000    # Réduit à 1000 pour un premier test rapide, augmentez à 5000 après

def generate_test_pairs(root_dir, test_ids, num_pairs):
    """Génère des paires équilibrées (50% similaires, 50% contrefaçons)."""
    X1, X2, Y = [], [], []
    temp_gen = SiameseTripletGenerator(root_dir, test_ids, batch_size=1) 
    identity_data = temp_gen._collect_identities()
    identity_ids = list(identity_data.keys())
    
    if not identity_ids:
        raise ValueError("Aucune donnée trouvée dans les dossiers de test.")

    count = 0
    while count < num_pairs:
        is_similar = (count % 2 == 0)
        id1 = random.choice(identity_ids)
        data = identity_data[id1]
        
        try:
            if is_similar:
                # Paire SIMILAIRE : Authentique vs Authentique
                if len(data['auth']) < 2: continue
                p1, p2 = random.sample(data['auth'], 2)
                label = 1
            else:
                # Paire DISSIMILAIRE : Authentique vs Contrefaçon (Forge)
                if len(data['auth']) < 1 or len(data['forg']) < 1: continue
                p1 = random.choice(data['auth'])
                p2 = random.choice(data['forg'])
                label = 0
                
            X1.append(preprocess_image(p1))
            X2.append(preprocess_image(p2))
            Y.append(label)
            count += 1
        except Exception:
            continue

    return np.array(X1), np.array(X2), np.array(Y)

def evaluate_siamese_model():
    print("\n--- 📊 Démarrage de l'Évaluation ---")
    
    # 1. Préparation des données de test
    _, test_ids = get_train_test_ids(ROOT_DATA_DIR, test_ratio=0.2)
    print(f"Identités de test (inconnues au modèle) : {len(test_ids)}")

    X_test_1, X_test_2, Y_test = generate_test_pairs(ROOT_DATA_DIR, test_ids, NUM_TEST_PAIRS)
    print(f"Paires de test générées : {len(Y_test)}")

    # 2. Chargement du modèle avec les custom_objects
    try:
        best_model = load_model(
            MODEL_PATH,
            custom_objects={
                'triplet_loss': triplet_loss,
                'normalize_embedding': normalize_embedding 
            }
        )
        # On extrait la branche commune pour l'inférence
        base_cnn = best_model.get_layer('Base_CNN')
        embedding_model = tf.keras.Model(inputs=base_cnn.input, outputs=base_cnn.output)
        print("✅ Modèle d'extraction chargé avec succès.")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")
        return

    # 3. Calcul des Embeddings
    print("Calcul des signatures numériques...")
    E1 = embedding_model.predict(X_test_1, verbose=1)
    E2 = embedding_model.predict(X_test_2, verbose=1)

    # 4. Calcul des distances Euclidiennes au carré
    distances_sq = np.sum(np.square(E1 - E2), axis=1)

    # 5. Calcul des métriques avancées
    print("\n" + "="*40)
    print("📈 RÉSULTATS DE L'ÉVALUATION")
    print("="*40)

    # Analyse des distances par classe
    dist_sim = distances_sq[Y_test == 1]
    dist_dissim = distances_sq[Y_test == 0]
    
    mean_sim = np.mean(dist_sim)
    mean_dissim = np.mean(dist_dissim)

    if np.max(distances_sq) == 0:
        print("⚠️ ALERTE : Toutes les distances sont à 0. Le modèle n'a pas appris.")
    else:
        # AUC Score : Capacité du modèle à donner une distance plus faible aux vrais qu'aux faux
        # (1 - distances_norm) car une distance faible = forte probabilité de similarité
        distances_norm = distances_sq / np.max(distances_sq)
        auc_score = roc_auc_score(Y_test, 1 - distances_norm)
        
        # Prédictions basées sur le seuil
        y_pred = (distances_sq < SEUIL_DE_DECISION).astype(int)
        acc = accuracy_score(Y_test, y_pred)
        f1 = f1_score(Y_test, y_pred)

        print(f"Distance Moyenne (Même auteur) : {mean_sim:.4f}")
        print(f"Distance Moyenne (Contrefaçons) : {mean_dissim:.4f}")
        print(f"Écart de séparation            : {abs(mean_dissim - mean_sim):.4f}")
        print("-" * 40)
        print(f"ROC AUC Score                  : {auc_score:.44f}")
        print(f"Précision (Accuracy)           : {acc:.4%}")
        print(f"F1-Score                       : {f1:.4f}")
    
    print("="*40)
    print("💡 ANALYSE : Pour rejeter plus de contrefaçons, diminuez le SEUIL_DE_DECISION.")

if __name__ == '__main__':
    evaluate_siamese_model()