import json
import jwt
from uuid import UUID
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from dependencies import SessionData, require_auth, get_pad_service, get_backup_service
from database.services.pad_service import PadService
from database.services.backup_service import BackupService
from database.config import DatabaseConfig
import posthog

canvas_router = APIRouter()

def get_default_canvas_data():
    try:
        with open("default_canvas.json", "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load default canvas: {str(e)}"
        )

@canvas_router.get("/default")
async def get_default_canvas(auth: SessionData = Depends(require_auth)):
    try:
        with open("default_canvas.json", "r") as f:
            canvas_data = json.load(f)
        return canvas_data
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load default canvas: {str(e)}"}
        )

@canvas_router.post("")
async def save_canvas(
    data: Dict[str, Any], 
    auth: SessionData = Depends(require_auth), 
    pad_service: PadService = Depends(get_pad_service),
    request: Request = None
):
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    user_id = decoded["sub"]
    
    # Generate a pad ID if not provided (you might want to handle this differently)
    pad_id = UUID(data.get("pad_id", "00000000-0000-0000-0000-000000000000"))
    
    success = await pad_service.store_pad_data(
        UUID(user_id), 
        pad_id, 
        data,
        backup_interval_seconds=DatabaseConfig.BACKUP_INTERVAL_SECONDS,
        max_backups_per_user=DatabaseConfig.MAX_BACKUPS_PER_USER
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save canvas data")
    return {"status": "success"}

@canvas_router.get("")
async def get_canvas(
    auth: SessionData = Depends(require_auth),
    pad_service: PadService = Depends(get_pad_service)
):
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    user_id = decoded["sub"]
    
    # Get all pads for this user
    pads = await pad_service.get_all_user_pads(UUID(user_id))
    
    if not pads:
        return get_default_canvas_data()
    
    # Return the first pad's data (or you could modify this to return a specific pad)
    return pads[0]["data"] if pads else get_default_canvas_data()

@canvas_router.get("/recent")
async def get_recent_canvas_backups(
    limit: int = DatabaseConfig.MAX_BACKUPS_PER_USER,
    auth: SessionData = Depends(require_auth),
    backup_service: BackupService = Depends(get_backup_service)
):
    """Get the most recent canvas backups for the authenticated user"""
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    user_id = decoded["sub"]
    
    # Limit the number of backups to the maximum configured value
    if limit > DatabaseConfig.MAX_BACKUPS_PER_USER:
        limit = DatabaseConfig.MAX_BACKUPS_PER_USER
    
    backups = await backup_service.get_recent_backups_by_user_id(UUID(user_id), limit)
    return {"backups": backups}
