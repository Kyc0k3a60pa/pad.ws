from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base_model import TimestampedBase
from ..config import DatabaseConfig

class User(TimestampedBase):
    """Model for users table in padws schema"""
    __tablename__ = "users"
    __table_args__ = {"schema": DatabaseConfig.APP_SCHEMA_NAME}
    
    username = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=False)
    jwt_id = Column(String, nullable=True, unique=True)
    
    pads = relationship("Pad", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"
