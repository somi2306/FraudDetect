# backend/app/training/train_yolo.py
from ultralytics import YOLO
import os

# Chemins d'accès. Le script est dans 'training', data.yaml est dans 'data/annotation'.
DATA_YAML_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "annotation", "data.yaml"
)) 

# Nom du projet, YOLO ajoutera un index (cheque_detection_cih, cheque_detection_cih2, etc.)
PROJECT_NAME = "cheque_detection_combined" 

def train_detection_model():
    """Charge un modèle pré-entraîné (YOLOv8n) et l'entraîne sur les données du chèque."""
    
    # Vérification essentielle avant le lancement
    if not os.path.exists(DATA_YAML_PATH):
        print(f"ERREUR FATALE: Le fichier data.yaml est introuvable à : {DATA_YAML_PATH}")
        return

    print("Chargement du modèle YOLOv8n...")
    model = YOLO('yolov8n.pt') 

    # 2. Entraînement
    print(f"Lancement de l'entraînement avec le fichier de données: {DATA_YAML_PATH}")
    
    results = model.train(
        data=DATA_YAML_PATH, 
        epochs=50,     # Augmentez à 100 ou plus pour un vrai résultat
        imgsz=640,       
        project=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "runs")),
        name=PROJECT_NAME,
        batch=16,        
        workers=8        
    )
    
    print("\n✅ Entraînement terminé.")
    # Le modèle sera sauvegardé dans runs/detect/cheque_detection_combined/weights/best.pt

if __name__ == '__main__':
    train_detection_model()