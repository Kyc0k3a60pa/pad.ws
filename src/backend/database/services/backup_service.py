from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.backup_repository import BackupRepository
from ..repositories.pad_repository import PadRepository

class BackupService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.backup_repo = BackupRepository(session)
        self.pad_repo = PadRepository(session)
    
    async def get_backups_by_pad_id(self, pad_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get backups for a pad"""
        backups = await self.backup_repo.get_by_pad_id(pad_id, limit)
        return [
            {
                "id": str(backup.id),
                "pad_id": str(backup.pad_id),
                "data": backup.data,
                "created_at": backup.created_at,
                "updated_at": backup.updated_at
            }
            for backup in backups
        ]
    
    async def get_recent_backups_by_user_id(self, user_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent backups for all pads belonging to a user"""
        from ..repositories.user_repository import UserRepository
        user_repo = UserRepository(self.session)
        
        # Get all pads for this user
        pads = await user_repo.get_all_pads_by_user_id(user_id)
        
        if not pads:
            return []
        
        # Get backups for each pad
        all_backups = []
        for pad in pads:
            backups = await self.backup_repo.get_by_pad_id(pad.id, limit)
            for backup in backups:
                all_backups.append({
                    "id": str(backup.id),
                    "pad_id": str(backup.pad_id),
                    "timestamp": backup.created_at,
                    "data": backup.data
                })
        
        # Sort by timestamp and limit
        all_backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_backups[:limit]
    
    async def create_backup_if_needed(
        self, 
        pad_id: UUID, 
        data: Dict[str, Any],
        backup_interval_seconds: int = 300,
        max_backups_per_user: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Create a backup if enough time has passed since the last backup.
        Also manages the number of backups by deleting old ones if needed.
        """
        try:
            # Get the most recent backup for this pad
            backups = await self.backup_repo.get_by_pad_id(pad_id, 1)
            latest_backup = backups[0] if backups else None
            
            # Determine if we should create a backup
            should_backup = False
            current_time = datetime.now()
            
            if latest_backup is None:
                # No previous backup exists, so create one
                should_backup = True
            else:
                # Check if enough time has passed since the last backup
                time_since_last_backup = (current_time - latest_backup.created_at).total_seconds()
                if time_since_last_backup >= backup_interval_seconds:
                    should_backup = True
            
            if should_backup:
                # Create new backup
                new_backup = await self.backup_repo.create(pad_id=pad_id, data=data)
                
                # Clean up old backups if needed
                await self.backup_repo.delete_old_backups(pad_id, max_backups_per_user)
                
                if new_backup:
                    return {
                        "id": str(new_backup.id),
                        "pad_id": str(new_backup.pad_id),
                        "data": new_backup.data,
                        "created_at": new_backup.created_at,
                        "updated_at": new_backup.updated_at
                    }
            
            return None
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
