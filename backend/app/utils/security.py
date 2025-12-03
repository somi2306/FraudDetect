from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, status
from typing import Dict
from ..core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuration du contexte de hachage (standard FastAPI/Python)
# Utilise bcrypt
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crée un jeton d'accès JWT pour l'authentification.
    """
    to_encode = data.copy()
    
    # 1. Définir l'expiration
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # 2. Encoder le jeton
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond au hachage stocké.
    Utilisé lors de la connexion.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hache un mot de passe en clair.
    Utilisé lors de la création et de la modification du mot de passe de l'Agent.
    """
    return pwd_context.hash(password)