from sqlalchemy import Column, JSON, ForeignKey, UUID
from sqlalchemy.orm import relationship

from .base_model import TimestampedBase
from ..config import DatabaseConfig

class Backup(TimestampedBase):
    """Model for backups table in padws schema"""
    __tablename__ = "backups"
    __table_args__ = {"schema": DatabaseConfig.APP_SCHEMA_NAME}
    
    pad_id = Column(UUID(as_uuid=True), ForeignKey(f"{DatabaseConfig.APP_SCHEMA_NAME}.pads.id"), nullable=False)
    data = Column(JSON, nullable=False)
    
    pad = relationship("Pad", back_populates="backups")
    
    def __repr__(self):
        return f"<Backup(id={self.id}, pad_id='{self.pad_id}')>"
