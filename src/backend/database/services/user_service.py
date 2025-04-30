from uuid import UUID
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.user_repository import UserRepository
from ..repositories.pad_repository import PadRepository

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.pad_repo = PadRepository(session)
    
    async def get_user_by_jwt_id(self, jwt_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by JWT ID"""
        user = await self.user_repo.get_by_jwt_id(jwt_id)
        if user:
            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "jwt_id": user.jwt_id,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        return None
    
    async def get_or_create_user_by_jwt_id(
        self, jwt_id: str, email: str, username: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a user by JWT ID or create if not exists"""
        user = await self.user_repo.get_by_jwt_id(jwt_id)
        
        if not user:
            # Create new user
            user = await self.user_repo.create(
                jwt_id=jwt_id,
                email=email,
                username=username
            )
            
            if not user:
                return None
        
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "jwt_id": user.jwt_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    
    async def get_user_pads(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all pads for a user"""
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
