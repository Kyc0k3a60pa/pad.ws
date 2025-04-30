from sqlalchemy import Column, JSON, ForeignKey, UUID
from sqlalchemy.orm import relationship

from .base_model import TimestampedBase
from ..config import DatabaseConfig

schema_name = DatabaseConfig.get_schema_name()

class BackupModel(TimestampedBase):
    """Model for backups table in padws schema"""
    __tablename__ = "backups"
    __table_args__ = {"schema": schema_name}
    
    pad_id = Column(UUID(as_uuid=True), ForeignKey(f"{schema_name}.pads.id"), nullable=False)
    data = Column(JSON, nullable=False)
    
    pad = relationship("PadModel", back_populates="backups")
    
    def __repr__(self):
        return f"<BackupModel(id={self.id}, pad_id='{self.pad_id}')>"
