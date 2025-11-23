# backend/app/training/train_yolo.py
from ultralytics import YOLO
import os

# Chemin vers le fichier de configuration YAML créé à l'Étape 1.2
# Ajustez ce chemin selon l'endroit où vous placez 'cih-zones/data.yaml'
# backend/app/training/train_yolo.py

# ... (le reste des imports et la fonction train_detection_model restent inchangés)

# Chemin vers le fichier de configuration YAML (CORRECTION APPORTÉE ICI)
# Le script est dans '.../app/training'. On remonte d'un niveau (..), puis on descend dans 'data/cih-zones'.
DATA_YAML_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "cih-zones", "data.yaml"
)) 

PROJECT_NAME = "cheque_detection_cih"

def train_detection_model():
    """Charge un modèle pré-entraîné (YOLOv8n) et l'entraîne sur les données du chèque."""
    
    # 1. Charger un modèle initial (YOLOv8n = nano, le plus rapide et léger)
    print("Chargement du modèle YOLOv8n...")
    model = YOLO('yolov8n.pt') 

    # 2. Entraînement
    print(f"Lancement de l'entraînement avec le fichier de données: {DATA_YAML_PATH}")
    results = model.train(
        data=DATA_YAML_PATH, 
        epochs=100,      # Nombre d'époques (à augmenter pour de meilleurs résultats)
        imgsz=640,       # Taille des images pour l'entraînement
        project=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "runs")),
        name=PROJECT_NAME,
        batch=16,        # Taille du lot (à ajuster selon votre VRAM/mémoire GPU)
        workers=8        # Nombre de travailleurs de données
    )
    
    print("\n✅ Entraînement terminé.")
    # Le modèle sera sauvegardé dans runs/detect/cheque_detection_cih/weights/best.pt

if __name__ == '__main__':
    train_detection_model()