from uuid import UUID
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.pad_repository import PadRepository
from ..repositories.user_repository import UserRepository
from .backup_service import BackupService

class PadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pad_repo = PadRepository(session)
        self.user_repo = UserRepository(session)
        self.backup_service = BackupService(session)
    
    async def get_pad_by_id(self, pad_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a pad by ID with its data"""
        pad_data = await self.pad_repo.get_pad_data_by_id(pad_id)
        if pad_data:
            pad = await self.pad_repo.get_by_id(pad_id)
            return {
                "id": str(pad.id),
                "user_id": str(pad.user_id),
                "data": pad_data,
                "created_at": pad.created_at,
                "updated_at": pad.updated_at
            }
        return None
    
    async def get_all_user_pads(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all pads for a user with their data"""
        pads = await self.user_repo.get_all_pads_by_user_id(user_id)
        return [
            {
                "id": str(pad.id),
                "user_id": str(pad.user_id),
                "data": pad.data,
                "created_at": pad.created_at,
                "updated_at": pad.updated_at
            } 
            for pad in pads
        ]
    
    async def store_pad_data(
        self, 
        user_id: UUID,
        pad_id: UUID, 
        data: Dict[str, Any],
        backup_interval_seconds: int = 300,
        max_backups_per_user: int = 10
    ) -> bool:
        """
        Store pad data for a specific pad, creating or updating as needed.
        Also creates backups according to the specified interval.
        """
        try:
            # Check if the pad exists
            pad = await self.pad_repo.get_by_id(pad_id)
            
            if pad:
                # Update existing pad
                success = await self.pad_repo.update(pad.id, data=data)
                if not success:
                    return False
            else:
                # Create new pad with the specified ID
                pad = await self.pad_repo.create(id=pad_id, user_id=user_id, data=data)
                if not pad:
                    return False
            
            # Create backup if needed
            await self.backup_service.create_backup_if_needed(
                pad_id=pad.id,
                data=data,
                backup_interval_seconds=backup_interval_seconds,
                max_backups_per_user=max_backups_per_user
            )
            
            return True
        except Exception as e:
            print(f"Error storing pad data: {e}")
            return False
