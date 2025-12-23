import tensorflow as tf
from tensorflow.keras.layers import (
    Input,
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Lambda,
    Concatenate
)
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
import tensorflow.keras.backend as K

# ============================================================
# 1) PARAMÈTRES GÉNÉRAUX DU MODÈLE
# ============================================================
# Dimensions fixes des images de signatures
IMG_HEIGHT = 100
IMG_WIDTH = 200

# Nombre de canaux :
# 1 => image en niveaux de gris (noir et blanc)
CHANNELS = 1

# Taille du vecteur numérique final représentant une signature
# Plus cette valeur est grande, plus la représentation est riche
EMBEDDING_DIM = 512


# ============================================================
# 2) NORMALISATION DES EMBEDDINGS
# ============================================================
def normalize_embedding(z):
    """
    Normalise un vecteur (embedding) pour que sa norme soit égale à 1.

    Pourquoi ?
    - On compare les signatures par distance
    - La normalisation évite que la "taille" du vecteur
      influence la comparaison
    - Seule la direction (le contenu) du vecteur compte
    """
    return K.l2_normalize(z, axis=1)


# ============================================================
# 3) RÉSEAU DE BASE (CNN) : IMAGE → EMBEDDING
# ============================================================
def create_base_cnn(input_shape):
    """
    Ce réseau prend UNE image de signature en entrée
    et la transforme en un vecteur numérique (embedding).

    Ce vecteur résume les caractéristiques importantes
    de la signature (structure, courbes, style d’écriture, etc.).
    """

    # Entrée du réseau : une image (100 x 200 x 1)
    input_layer = Input(shape=input_shape, name='input_image')

    # --------------------------------------------------------
    # Bloc 1 : extraction de motifs simples
    # (traits, bords, lignes)
    # --------------------------------------------------------
    x = Conv2D(
        64,                # nombre de filtres
        (5, 5),            # taille du filtre
        activation='relu', # fonction non linéaire
        kernel_regularizer=l2(2e-4)  # limite le sur-apprentissage
    )(input_layer)

    # Réduction de la taille spatiale (moins de calculs)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # --------------------------------------------------------
    # Bloc 2 : motifs plus complexes
    # (formes, intersections, courbures)
    # --------------------------------------------------------
    x = Conv2D(
        128,
        (3, 3),
        activation='relu',
        kernel_regularizer=l2(2e-4)
    )(x)

    x = MaxPooling2D(pool_size=(2, 2))(x)

    # --------------------------------------------------------
    # Bloc 3 : motifs abstraits et globaux
    # --------------------------------------------------------
    x = Conv2D(
        256,
        (3, 3),
        activation='relu',
        kernel_regularizer=l2(2e-4)
    )(x)

    x = MaxPooling2D(pool_size=(2, 2))(x)

    # --------------------------------------------------------
    # Passage de la représentation 2D vers un vecteur 1D
    # --------------------------------------------------------
    x = Flatten()(x)

    # --------------------------------------------------------
    # Couche dense finale :
    # transforme les informations extraites en un vecteur de 512 valeurs
    # --------------------------------------------------------
    x = Dense(
        EMBEDDING_DIM,
        activation='relu',
        kernel_regularizer=l2(1e-3)
    )(x)

    # --------------------------------------------------------
    # Normalisation du vecteur (embedding)
    # --------------------------------------------------------
    x = Lambda(normalize_embedding, name='embedding_output')(x)

    # Modèle final : Image → Embedding
    return Model(
        inputs=input_layer,
        outputs=x,
        name="Base_CNN"
    )


# ============================================================
# 4) MODÈLE SIAMOIS AVEC TRIPLETS
# ============================================================
def create_siamese_model(base_cnn):
    """
    Ce modèle reçoit TROIS images de signatures :
    - Anchor   : signature authentique
    - Positive : autre signature authentique (même personne)
    - Negative : signature falsifiée

    Il utilise le même réseau (base_cnn) pour les trois images
    afin de produire trois embeddings comparables.
    """

    input_shape = (IMG_HEIGHT, IMG_WIDTH, CHANNELS)

    # Entrées du modèle
    input_A = Input(shape=input_shape, name='anchor_input')
    input_P = Input(shape=input_shape, name='positive_input')
    input_N = Input(shape=input_shape, name='negative_input')

    # --------------------------------------------------------
    # Passage des trois images dans le MÊME réseau de base
    # (poids partagés)
    # --------------------------------------------------------
    embedding_A = base_cnn(input_A)
    embedding_P = base_cnn(input_P)
    embedding_N = base_cnn(input_N)

    # --------------------------------------------------------
    # Fusion des trois embeddings en un seul vecteur
    # [A | P | N]
    #
    # Ce vecteur sera utilisé par la Triplet Loss
    # pour calculer les distances
    # --------------------------------------------------------
    merged_output = Concatenate(axis=-1)(
        [embedding_A, embedding_P, embedding_N]
    )

    # Modèle final Siamois
    return Model(
        inputs=[input_A, input_P, input_N],
        outputs=merged_output,
        name="Siamese_Triplet_Net"
    )
