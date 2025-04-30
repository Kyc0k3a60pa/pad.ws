from sqlalchemy import Column, String, JSON, ForeignKey, UUID
from sqlalchemy.orm import relationship

from .base_model import TimestampedBase
from ..config import DatabaseConfig

class PadModel(TimestampedBase):
    """Model for pads table in padws schema"""
    __tablename__ = "pads"
    __table_args__ = {"schema": DatabaseConfig.APP_SCHEMA_NAME}
    
    user_id = Column(UUID(as_uuid=True), ForeignKey(f"{DatabaseConfig.APP_SCHEMA_NAME}.users.id"), nullable=False)
    data = Column(JSON, nullable=False)
    
    user = relationship("UserModel", back_populates="pads")
    backups = relationship("BackupModel", back_populates="pad", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PadModel(id='{self.id}', user_id='{self.user_id}')>"
