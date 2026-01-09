# backend/app/routes/cheques.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..utils.auth import get_current_user
from ..core.db import get_db
from ..core.config import supabase
from ..models.user import User

router = APIRouter()


class ChequeDetail(BaseModel):
    numero_cheque: str
    montant_cheque: float


class ChequeResponse(BaseModel):
    id: int
    image_url: str
    date_depot: str
    status: Optional[str]
    banque_nom: Optional[str]
    numero_cheque: Optional[str]
    montant_cheque: Optional[float]


class ChequeStats(BaseModel):
    pending: int
    approved: int
    rejected: int


class ChequeCreateResponse(BaseModel):
    id: int
    message: str


@router.post("/upload", response_model=ChequeCreateResponse)
async def upload_cheque(
    banque_name: str = Form(None),
    banque_code: str = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new cheque
    
    Args:
        banque_name: Nom de la banque (ex: "CIH Banque") - optionnel
        banque_code: Code de banque (ex: "230", "007", "145") - optionnel
        file: Fichier image du chèque
        
    Note: Fournir soit banque_name soit banque_code
    """
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Récupère ou crée l'utilisateur en base locale
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        from ..models.user import UserRole
        user = User(
            clerk_id=clerk_id,
            email=current_user.get("email", ""),
            role=UserRole.BENEFICIAIRE,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    user_id = user.id

    # Déterminer le bank_id à partir du code ou du nom
    if banque_code:
        # Si un code de banque est fourni, l'utiliser
        from ..utils.bank_codes import get_bank_id_from_code
        try:
            bank_id = get_bank_id_from_code(banque_code)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif banque_name:
        # Sinon, utiliser le nom de la banque
        bank_response = supabase.table("banks").select("id").eq("name", banque_name).execute()
        if not bank_response.data or len(bank_response.data) == 0:
            raise HTTPException(status_code=400, detail=f"Bank '{banque_name}' not found")
        bank_id = bank_response.data[0]["id"]
    else:
        raise HTTPException(status_code=400, detail="Fournir soit 'banque_name' soit 'banque_code'")

    # Upload image to Supabase Storage
    try:
        file_content = await file.read()
        file_ext = file.filename.split('.')[-1] if file.filename else 'png'
        file_name = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Try to create bucket if it doesn't exist
        try:
            supabase.storage.create_bucket("cheques", options={"public": True})
        except Exception:
            pass  # Bucket may already exist
        
        # Upload to storage bucket 'cheques'
        storage_response = supabase.storage.from_("cheques").upload(
            file_name,
            file_content,
            {"content-type": file.content_type or "image/png"}
        )
        
        # Get public URL
        image_url = supabase.storage.from_("cheques").get_public_url(file_name)
    except Exception as e:
        print(f"Storage upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    # Insert cheque record
    try:
        cheque_data = {
            "image_url": image_url,
            "date_depot": datetime.now().isoformat(),
            "beneficiaire_id": user_id,
            "banque_cible_id": bank_id,
            "status": "pending",
        }
        
        cheque_response = supabase.table("cheques").insert(cheque_data).execute()
        
        if not cheque_response.data:
            raise HTTPException(status_code=500, detail="Failed to create cheque record")
        
        cheque_id = cheque_response.data[0]["id"]
        
        return {
            "id": cheque_id,
            "message": "Chèque téléchargé avec succès"
        }
    except Exception as e:
        print(f"Database insert error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save cheque: {str(e)}")


@router.get("/banks")
async def get_banks(current_user: dict = Depends(get_current_user)):
    """Get list of available banks"""
    banks_response = supabase.table("banks").select("id, name").execute()
    return banks_response.data or []


@router.get("/mes-cheques", response_model=List[ChequeResponse])
async def get_my_cheques(current_user: dict = Depends(get_current_user)):
    """Get all cheques for the current beneficiary"""
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the user's internal ID from clerk_id
    try:
        user_response = supabase.table("users").select("id").eq("clerk_id", clerk_id).execute()
        if not user_response.data or len(user_response.data) == 0:
            # User exists in Clerk but not in Supabase users table yet
            # Return empty list for now
            return []
        user_id = user_response.data[0]["id"]
    except Exception as e:
        print(f"Erreur lors de la recherche utilisateur Supabase: {e}")
        # Return empty list if user not found in Supabase
        return []

    # Get cheques with bank name and details
    cheques_response = supabase.table("cheques")\
        .select("id, image_url, date_depot, status, banque_cible_id, banks(name)")\
        .eq("beneficiaire_id", user_id)\
        .order("date_depot", desc=True)\
        .execute()

    cheques = cheques_response.data or []

    # Get details for each cheque
    result = []
    for cheque in cheques:
        # Use maybeSingle equivalent - don't use .single() as it throws if no result
        detail_response = supabase.table("details_cheques")\
            .select("numero_cheque, montant_cheque")\
            .eq("cheque_id", cheque["id"])\
            .limit(1)\
            .execute()
        
        detail = detail_response.data[0] if detail_response.data else {}
        
        result.append({
            "id": cheque["id"],
            "image_url": cheque["image_url"],
            "date_depot": cheque["date_depot"],
            "status": cheque["status"],
            "banque_nom": cheque.get("banks", {}).get("name") if cheque.get("banks") else None,
            "numero_cheque": detail.get("numero_cheque"),
            "montant_cheque": detail.get("montant_cheque"),
        })

    return result


@router.get("/stats")
async def get_cheque_stats(current_user: dict = Depends(get_current_user)):
    """Get cheque statistics for the current beneficiary"""
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the user's internal ID
    try:
        user_response = supabase.table("users").select("id").eq("clerk_id", clerk_id).execute()
        if not user_response.data or len(user_response.data) == 0:
            # User exists in Clerk but not in Supabase users table yet
            return {"pending": 0, "approved": 0, "rejected": 0}
        user_id = user_response.data[0]["id"]
    except Exception as e:
        print(f"Erreur lors de la recherche utilisateur: {e}")
        return {"pending": 0, "approved": 0, "rejected": 0}

    # Count by status
    pending_response = supabase.table("cheques")\
        .select("id", count="exact")\
        .eq("beneficiaire_id", user_id)\
        .eq("status", "pending")\
        .execute()
    
    approved_response = supabase.table("cheques")\
        .select("id", count="exact")\
        .eq("beneficiaire_id", user_id)\
        .eq("status", "approved")\
        .execute()
    
    rejected_response = supabase.table("cheques")\
        .select("id", count="exact")\
        .eq("beneficiaire_id", user_id)\
        .eq("status", "rejected")\
        .execute()

    return {
        "pending": pending_response.count or 0,
        "approved": approved_response.count or 0,
        "rejected": rejected_response.count or 0,
    }


@router.get("/{cheque_id}")
async def get_cheque_detail(cheque_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific cheque by ID"""
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get user ID
    try:
        user_response = supabase.table("users").select("id").eq("clerk_id", clerk_id).execute()
        if not user_response.data or len(user_response.data) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_response.data[0]["id"]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la recherche utilisateur: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    # Get the cheque
    cheque_response = supabase.table("cheques")\
        .select("id, image_url, date_depot, status, banque_cible_id, banks(name)")\
        .eq("id", cheque_id)\
        .eq("beneficiaire_id", user_id)\
        .single()\
        .execute()

    if not cheque_response.data:
        raise HTTPException(status_code=404, detail="Cheque not found")

    cheque = cheque_response.data

    # Get details
    detail_response = supabase.table("details_cheques")\
        .select("numero_cheque, montant_cheque")\
        .eq("cheque_id", cheque_id)\
        .single()\
        .execute()
    
    detail = detail_response.data if detail_response.data else {}

    return {
        "id": cheque["id"],
        "image_url": cheque["image_url"],
        "date_depot": cheque["date_depot"],
        "status": cheque["status"],
        "banque_nom": cheque.get("banks", {}).get("name") if cheque.get("banks") else None,
        "numero_cheque": detail.get("numero_cheque"),
        "montant_cheque": detail.get("montant_cheque"),
    }
