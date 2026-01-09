# backend/app/training/split_data.py
import os
import random

# Chemins d'accès. Le script est dans 'training', le dossier de données est dans 'data/annotation'
ANNOTATION_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "annotation"
))

INPUT_FILE = os.path.join(ANNOTATION_DIR, "Train.txt")
OUTPUT_TRAIN_FILE = os.path.join(ANNOTATION_DIR, "train_80.txt")
OUTPUT_VAL_FILE = os.path.join(ANNOTATION_DIR, "val_20.txt")

# Ratio de séparation
SPLIT_RATIO = 0.80  # 80% pour l'entraînement

def split_data(input_file, train_file, val_file, ratio):
    """Lit le fichier d'entrée et le divise en deux ensembles (train/val) selon le ratio."""
    try:
        with open(input_file, 'r') as f:
            all_paths = f.readlines()
    except FileNotFoundError:
        print(f"ERREUR: Fichier d'entrée {input_file} introuvable.")
        return

    # Nettoyer les chemins (supprimer les espaces et sauts de ligne)
    all_paths = [path.strip() for path in all_paths if path.strip()]
    
    if not all_paths:
        print("ERREUR: Le fichier d'entrée est vide.")
        return

    # Mélanger les chemins pour assurer une répartition aléatoire
    random.shuffle(all_paths)
    
    # Calculer le point de séparation
    split_point = int(len(all_paths) * ratio)
    
    # Séparer les ensembles
    train_paths = all_paths[:split_point]
    val_paths = all_paths[split_point:]

    # Écrire les fichiers de sortie
    with open(train_file, 'w') as f:
        f.write('\n'.join(train_paths))
        
    with open(val_file, 'w') as f:
        f.write('\n'.join(val_paths))
        
    print(f"\n✅ Séparation des données terminée. Total: {len(all_paths)}")
    print(f"   - Entraînement (80%): {len(train_paths)} images -> {os.path.basename(train_file)}")
    print(f"   - Validation (20%): {len(val_paths)} images -> {os.path.basename(val_file)}")

if __name__ == "__main__":
    split_data(INPUT_FILE, OUTPUT_TRAIN_FILE, OUTPUT_VAL_FILE, SPLIT_RATIO)