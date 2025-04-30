from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.user_model import UserModel
from ..models.pad_model import PadModel
from .base_repository import BaseRepository

class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)
    
    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username"""
        try:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email"""
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None
        
    async def get_by_jwt_id(self, jwt_id: str) -> Optional[UserModel]:
        """Get a user by JWT ID"""
        try:
            stmt = select(UserModel).where(UserModel.jwt_id == jwt_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by JWT ID: {e}")
            return None

    async def get_all_pads_by_user_id(self, user_id: UUID) -> List[PadModel]:
        """Get all pads for a user"""
        try:
            stmt = select(PadModel).where(PadModel.user_id == user_id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            print(f"Error retrieving pads by user_id: {e}")
            return []
