import os
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import Sequence
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Configuration  des dimension des images input pour etre de meme dimension
IMG_HEIGHT = 100 
IMG_WIDTH = 200
CHANNELS = 1 # Niveaux de Gris

#les images seront pris apartir du fichier train c'est lui qui contient le chemin vers le dossier 

def preprocess_image(path):
    """
    Charge, redimensionne en conservant le ratio, ajoute du padding et normalise une image.
    """
    # 1. Charger l'image en niveaux de gris
    img = Image.open(path).convert('L')
    original_w, original_h = img.size
    
    target_h, target_w = IMG_HEIGHT, IMG_WIDTH

    # 2. Calculer le ratio de redimensionnement
    # Utiliser le ratio minimum pour que l'image tienne dans la taille cible
    ratio = min(target_w / original_w, target_h / original_h)
    
    # Nouvelles dimensions (en conservant le ratio)
    new_w = int(original_w * ratio)
    new_h = int(original_h * ratio)

    # 3. Redimensionner l'image
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 4. Créer un nouveau canevas noir pour le padding
    # Le 'L' signifie mode niveaux de gris (valeur 0 est noir)
    new_img = Image.new('L', (target_w, target_h), 0)

    # 5. Calculer la position pour centrer l'image
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    
    # Coller l'image redimensionnée sur le canevas noir
    new_img.paste(img, (x_offset, y_offset))

    # 6. Convertir en tableau numpy et normaliser
    img_array = np.array(new_img, dtype=np.float32)
    # Ajouter la dimension du canal (1)
    img_array = np.expand_dims(img_array, axis=-1)
    # Normaliser les pixels (0 à 1)
    img_array = img_array / 255.0
    
    return img_array
#on passe a la generation des triplets des signatures  
class SiameseTripletGenerator(Sequence):
    def __init__(self, root_dir, signataire_ids, batch_size):
        self.root_dir = root_dir
        self.signataire_ids = signataire_ids
        self.batch_size = batch_size
        self.identities = self._collect_identities()
        # Calcule le nombre de lots (epochs)
        self.steps_per_epoch = 1000 # Un nombre arbitraire élevé de triplets par epoch
        
    def _collect_identities(self):
        """Récolte tous les chemins de fichiers par identité et type (auth/forg)."""
        identities_data = {}
        for id in self.signataire_ids:
            auth_dir = os.path.join(self.root_dir, id)
            forg_dir = os.path.join(self.root_dir, id + '_forg')
            
            auth_files = [os.path.join(auth_dir, f) for f in os.listdir(auth_dir) if f.endswith(('.png', '.jpg'))]
            forg_files = [os.path.join(forg_dir, f) for f in os.listdir(forg_dir) if f.endswith(('.png', '.jpg'))]
            
            # S'assurer d'avoir au moins 2 vraies et 1 fausse pour créer un triplet
            if len(auth_files) >= 2 and len(forg_files) >= 1:
                identities_data[id] = {'auth': auth_files, 'forg': forg_files}
                
        if not identities_data:
            raise ValueError("Aucune identité valide trouvée avec assez d'images pour créer des triplets.")
        
        print(f"Dataset initialisé avec {len(identities_data)} signataires valides.")
        return identities_data

    def __len__(self):
        """Retourne le nombre de lots par epoch."""
        return self.steps_per_epoch

    def __getitem__(self, index):
        """Génère un lot (batch) de triplets (A, P, N)"""
        
        A_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))
        P_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))
        N_batch = np.zeros((self.batch_size, IMG_HEIGHT, IMG_WIDTH, CHANNELS))
        
        # Le Triplet Loss est sans étiquette (y_true) donc nous retournons un tableau de zéros
        dummy_y = np.zeros((self.batch_size, EMBEDDING_DIM)) 
        
        identity_ids = list(self.identities.keys())

        for i in range(self.batch_size):
            # 1. Sélectionner une identité aléatoire
            anchor_id = random.choice(identity_ids)
            id_data = self.identities[anchor_id]

            # 2. Choisir A et P (Authentiques)
            anchor_path, positive_path = random.sample(id_data['auth'], 2)
            
            # 3. Choisir N (Contrefaçon)
            negative_path = random.choice(id_data['forg'])
            
            # Charger et prétraiter
            A_batch[i] = preprocess_image(anchor_path)
            P_batch[i] = preprocess_image(positive_path)
            N_batch[i] = preprocess_image(negative_path)

        # Keras/TensorFlow attend [inputs], [outputs]
        return [A_batch, P_batch, N_batch], [dummy_y, dummy_y, dummy_y]

# --- Utilitaire pour la séparation des IDs ---
def get_train_test_ids(root_dir, test_ratio=0.2):
    """Liste tous les IDs et les sépare en entraînement et test."""
    all_dirs = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    
    # Filtrer uniquement les dossiers '00X' (Authentique) et enlever les '_forg'
    unique_ids = sorted(list(set([d.split('_')[0] for d in all_dirs])))
    
    random.shuffle(unique_ids)
    
    test_size = int(len(unique_ids) * test_ratio)
    train_ids = unique_ids[test_size:]
    test_ids = unique_ids[:test_size]
    
    return train_ids, test_ids