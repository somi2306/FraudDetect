import hmac
import hashlib
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.core.config import supabase

WEBHOOK_TOLERANCE_SECONDS = 5 * 60  # 5 minutes


def verify_clerk_signature(body: str, signature_header: Optional[str], secret: str, tolerance: int = WEBHOOK_TOLERANCE_SECONDS) -> bool:
    if not signature_header:
        return False

    try:
        parts = dict(pair.split("=", 1) for pair in signature_header.split(",") if "=" in pair)
        timestamp = int(parts.get("t", "0"))
        expected_signature = parts.get("v1")

        if not timestamp or not expected_signature:
            return False

        if abs(time.time() - timestamp) > tolerance:
            return False

        signed_payload = f"{timestamp}.{body}"
        computed_signature = hmac.new(secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_signature, expected_signature)
    except Exception:
        return False


def _pick_email(attributes: Dict[str, Any]) -> Optional[str]:
    if email := attributes.get("primary_email_address"):
        return email

    emails = attributes.get("email_addresses")
    if isinstance(emails, List) and emails:
        for entry in emails:
            if isinstance(entry, dict) and entry.get("email_address"):
                return entry.get("email_address")

    return attributes.get("email")


def _pick_metadata_field(metadata: Dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        if value := metadata.get(key):
            return value
    return None


def build_clerk_user_payload(event_body: Dict[str, Any]) -> Dict[str, Optional[str]]:
    data = event_body.get("data") or {}
    attributes = data.get("attributes") or data.get("object") or {}
    metadata = attributes.get("unsafe_metadata") or {}

    def _normalize_role(value: Optional[str]) -> str:
        lookup = {
            "bénéficiaire": "BENEFICIAIRE",
            "beneficiaire": "BENEFICIAIRE",
            "beneficiary": "BENEFICIAIRE",
            "agent": "AGENT",
            "admin": "ADMIN",
        }
        if not value:
            return "BENEFICIAIRE"
        return lookup.get(str(value).strip().lower(), "BENEFICIAIRE")

    clerk_id = data.get("id") or attributes.get("id")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clerk event missing user identifier",
        )

    return {
        "clerk_id": clerk_id,
        "email": _pick_email(attributes),
        "first_name": attributes.get("first_name") or attributes.get("firstName"),
        "last_name": attributes.get("last_name") or attributes.get("lastName"),
        "image_url": attributes.get("profile_image_url") or attributes.get("image_url"),
        "cin": _pick_metadata_field(metadata, "cin", "CIN"),
        "rib": _pick_metadata_field(metadata, "rib", "RIB"),
        "phone": _pick_metadata_field(metadata, "phone", "phone_number", "telephone"),
        "role": _normalize_role(metadata.get("role") or metadata.get("user_role")),
    }


def upsert_clerk_user(payload: Dict[str, Optional[str]]) -> Dict[str, Any]:
    try:
        response = supabase.table("users").upsert([payload], on_conflict="clerk_id").execute()
    except Exception as exc:
        print("Supabase upsert exception:", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur Supabase: {exc}")

    # supabase-py v2 uses response.data; errors raise exceptions
    if not response.data:
        print("Supabase upsert returned no data")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert returned no data")

    return response.data[0] if response.data else {}
