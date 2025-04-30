from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base_model import TimestampedBase
from ..config import DatabaseConfig

schema_name = DatabaseConfig.get_schema_name()

class UserModel(TimestampedBase):
    """Model for users table in app schema"""
    __tablename__ = "users"
    __table_args__ = {"schema": schema_name}
    
    username = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=False)
    jwt_id = Column(String, nullable=True, unique=True)
    
    pads = relationship("PadModel", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserModel(id='{self.id}', username='{self.username}', email='{self.email}')>"
