import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
import tensorflow.keras.backend as K

# --- Hyperparamètres (À ajuster si besoin) ---
IMG_HEIGHT = 100
IMG_WIDTH = 200
CHANNELS = 1  # 1 pour Niveaux de Gris
EMBEDDING_DIM = 512 

def create_base_cnn(input_shape):
    """
    Crée le modèle CNN de base (l'extracteur de caractéristiques).
    """
    input_layer = Input(shape=input_shape, name='input_image')

    # Couche 1: 64 filtres
    x = Conv2D(64, (5, 5), activation='relu', kernel_regularizer=l2(2e-4))(input_layer)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # Couche 2: 128 filtres
    x = Conv2D(128, (3, 3), activation='relu', kernel_regularizer=l2(2e-4))(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    # Couche 3: 256 filtres
    x = Conv2D(256, (3, 3), activation='relu', kernel_regularizer=l2(2e-4))(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    # Flattening et couche Dense pour l'Embedding
    x = Flatten()(x)
    x = Dense(EMBEDDING_DIM, activation='relu', kernel_regularizer=l2(1e-3))(x)
    
    # Normalisation L2: Cruciale pour la Triplet Loss
    x = Lambda(lambda z: K.l2_normalize(z, axis=1), name='embedding_output')(x)

    return Model(inputs=input_layer, outputs=x, name="Base_CNN")

def create_siamese_model(base_cnn):
    """
    Crée le modèle siamois avec les trois branches.
    """
    input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)
    
    # Définir les trois entrées
    input_A = Input(shape=input_shape, name='anchor_input')
    input_P = Input(shape=input_shape, name='positive_input')
    input_N = Input(shape=input_shape, name='negative_input')

    # Partager le CNN sur chaque entrée
    embedding_A = base_cnn(input_A)
    embedding_P = base_cnn(input_P)
    embedding_N = base_cnn(input_N)

    # Le modèle complet prend les trois entrées et sort les trois embeddings
    siamese_net = Model(inputs=[input_A, input_P, input_N], 
                        outputs=[embedding_A, embedding_P, embedding_N],
                        name="Siamese_Triplet_Net")
    
    return siamese_net

if __name__ == '__main__':
    # Test rapide de l'architecture
    base_cnn = create_base_cnn(input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS))
    siamese_model = create_siamese_model(base_cnn)
    siamese_model.summary()