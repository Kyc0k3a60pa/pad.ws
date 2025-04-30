from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.backup_model import Backup
from .base_repository import BaseRepository

class BackupRepository(BaseRepository[Backup]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Backup)
    
    async def get_by_pad_id(self, pad_id: UUID, limit: int = 10) -> List[Backup]:
        """Get backups for a pad"""
        try:
            stmt = select(Backup).where(Backup.pad_id == pad_id).order_by(Backup.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            print(f"Error retrieving backups by pad_id: {e}")
            return []
    
    async def delete_old_backups(self, pad_id: UUID, keep_count: int = 10) -> bool:
        """Delete old backups, keeping only the most recent ones"""
        try:
            # Get all backups for the pad
            stmt = select(Backup).where(Backup.pad_id == pad_id).order_by(Backup.created_at.desc())
            result = await self.session.execute(stmt)
            backups = list(result.scalars().all())
            
            # If we have more backups than we want to keep
            if len(backups) > keep_count:
                # Delete the oldest backups
                for backup in backups[keep_count:]:
                    await self.session.delete(backup)
                
                await self.session.commit()
            
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error deleting old backups: {e}")
            return False
