from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from ..models.base_model import TimestampedBase

T = TypeVar('T', bound=TimestampedBase)

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get an entity by ID"""
        try:
            stmt = select(self.model_class).where(self.model_class.id == id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            print(f"Error retrieving {self.model_class.__name__}: {e}")
            return None
    
    async def get_all(self) -> List[T]:
        """Get all entities"""
        try:
            stmt = select(self.model_class)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            print(f"Error retrieving all {self.model_class.__name__}s: {e}")
            return []
    
    async def create(self, **kwargs) -> Optional[T]:
        """Create a new entity"""
        try:
            entity = self.model_class(**kwargs)
            self.session.add(entity)
            await self.session.commit()
            return entity
        except Exception as e:
            await self.session.rollback()
            print(f"Error creating {self.model_class.__name__}: {e}")
            return None
    
    async def update(self, id: UUID, **kwargs) -> bool:
        """Update an entity"""
        try:
            if not kwargs:
                return True  # Nothing to update
                
            stmt = update(self.model_class).where(self.model_class.id == id).values(**kwargs)
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error updating {self.model_class.__name__}: {e}")
            return False
    
    async def delete(self, id: UUID) -> bool:
        """Delete an entity"""
        try:
            stmt = delete(self.model_class).where(self.model_class.id == id)
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error deleting {self.model_class.__name__}: {e}")
            return False
