from uuid import UUID
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.pad_model import PadModel
from .base_repository import BaseRepository

class PadRepository(BaseRepository[PadModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PadModel)
        
    async def get_pad_data_by_id(self, pad_id: UUID) -> Optional[Dict[str, Any]]:
        """Get pad data by ID"""
        try:
            pad = await self.get_by_id(pad_id)
            if pad:
                return pad.data
            return None
        except Exception as e:
            print(f"Error retrieving pad data: {e}")
            return None
