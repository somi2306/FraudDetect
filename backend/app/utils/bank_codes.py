# backend/app/utils/bank_codes.py
"""
Mapping des codes de banque vers les IDs de la base de données.
Codes de banque Marocains vers les IDs de notre table banks.
"""

# Mapping: code_banque -> bank_id
BANK_CODE_TO_ID = {
    "230": 17,      # CIH Banque
    "007": 18,      # Attijariwafa Banque
    "145": 19,      # Banque Populaire
}

# Mapping inverse: bank_id -> code_banque
BANK_ID_TO_CODE = {v: k for k, v in BANK_CODE_TO_ID.items()}


def get_bank_id_from_code(bank_code: str) -> int:
    code_str = str(bank_code).strip()
    if code_str not in BANK_CODE_TO_ID:
        # On log l'erreur ici pour être sûr
        print(f"DEBUG: Code banque '{code_str}' introuvable dans {list(BANK_CODE_TO_ID.keys())}")
        raise ValueError(f"Code banque '{code_str}' non reconnu.")
    return BANK_CODE_TO_ID[code_str]


def get_bank_code_from_id(bank_id: int) -> str:
    """
    Récupère le code de banque à partir de l'ID de la banque.
    
    Args:
        bank_id: ID de la banque dans la base de données
    
    Returns:
        str: Code de banque
        
    Raises:
        ValueError: Si l'ID de banque n'est pas reconnu
    """
    if bank_id not in BANK_ID_TO_CODE:
        available = ", ".join(BANK_ID_TO_CODE.keys())
        raise ValueError(f"ID de banque '{bank_id}' non reconnu. IDs disponibles: {available}")
    
    return BANK_ID_TO_CODE[bank_id]
