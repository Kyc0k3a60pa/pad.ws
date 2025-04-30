from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.user_model import User
from ..models.pad_model import Pad
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        try:
            stmt = select(User).where(User.username == username)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None
        
    async def get_by_jwt_id(self, jwt_id: str) -> Optional[User]:
        """Get a user by JWT ID"""
        try:
            stmt = select(User).where(User.jwt_id == jwt_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving user by JWT ID: {e}")
            return None

    async def get_all_pads_by_user_id(self, user_id: UUID) -> List[Pad]:
        """Get all pads for a user"""
        try:
            stmt = select(Pad).where(Pad.user_id == user_id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            print(f"Error retrieving pads by user_id: {e}")
            return []