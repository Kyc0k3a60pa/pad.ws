import json
import jwt
from uuid import UUID
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from dependencies import SessionData, require_auth, get_pad_service, get_backup_service, get_user_service
from database.services.pad_service import PadService
from database.services.backup_service import BackupService
from database.services.user_service import UserService
from database.config import DatabaseConfig

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
    user_service: UserService = Depends(get_user_service),
    request: Request = None
):
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    jwt_id = decoded["sub"]
    
    # Look up the user by jwt_id to get the actual user_id
    user = await user_service.get_by_jwt_id(jwt_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a pad ID if not provided (you might want to handle this differently)
    pad_id = UUID(data["appState"]["pad"]["uniqueId"])
    user_id = UUID(user["id"])

    print(f"Saving canvas data for user {user_id} with pad ID {pad_id}")

    success = await pad_service.store_pad_data(
        user_id,
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
    user_service: UserService = Depends(get_user_service),
):
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    jwt_id = decoded["sub"]
    
    # Look up the user by jwt_id to get the actual user_id
    user = await user_service.get_by_jwt_id(jwt_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all pads for this user
    pads = await user_service.get_pads(user["id"])
    
    if not pads:
        return get_default_canvas_data()
    
    # Return the first pad's data (or you could modify this to return a specific pad)
    return pads[0]["data"] if pads else get_default_canvas_data()

@canvas_router.get("/recent")
async def get_recent_canvas_backups(
    limit: int = DatabaseConfig.MAX_BACKUPS_PER_USER,
    auth: SessionData = Depends(require_auth),
    backup_service: BackupService = Depends(get_backup_service),
    user_service: UserService = Depends(get_user_service)
):
    """Get the most recent canvas backups for the authenticated user"""
    access_token = auth.token_data.get("access_token")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    jwt_id = decoded["sub"]
    
    # Look up the user by jwt_id to get the actual user_id
    user = await user_service.get_by_jwt_id(jwt_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Limit the number of backups to the maximum configured value
    if limit > DatabaseConfig.MAX_BACKUPS_PER_USER:
        limit = DatabaseConfig.MAX_BACKUPS_PER_USER
    
    backups = await backup_service.get_recent_backups_by_user_id(user["id"], limit)
    return {"backups": backups}
