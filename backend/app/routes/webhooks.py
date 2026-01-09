import json
import os
from fastapi import APIRouter, HTTPException, Request, status

from app.services.clerk_sync_service import (
    verify_clerk_signature,
    build_clerk_user_payload,
    upsert_clerk_user,
)

router = APIRouter(tags=["Clerk Webhooks"])


@router.post("/clerk")
async def clerk_webhook(request: Request):
    secret = os.environ.get("CLERK_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_WEBHOOK_SECRET must be configured",
        )

    signature = request.headers.get("Clerk-Signature") or request.headers.get("clerk-signature")
    body_bytes = await request.body()

    try:
        payload_text = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode webhook payload",
        )

    if not verify_clerk_signature(payload_text, signature, secret):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Clerk webhook signature")

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook payload is not valid JSON")

    event_type = payload.get("type")
    if event_type not in {"user.created", "user.updated"}:
        return {"status": "ignored", "event": event_type}

    user_payload = build_clerk_user_payload(payload)
    synced_record = upsert_clerk_user(user_payload)

    return {
        "status": "synced",
        "event": event_type,
        "clerk_id": user_payload["clerk_id"],
        "record_id": synced_record.get("id") if isinstance(synced_record, dict) else None,
    }
