from sqlalchemy import Column, String, JSON, ForeignKey, UUID
from sqlalchemy.orm import relationship

from .base import TimestampedBase

class Pad(TimestampedBase):
    """Model for pads table in padws schema"""
    __tablename__ = "pads"
    __table_args__ = {"schema": "padws"}
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("padws.users.id"), nullable=False)
    data = Column(JSON, nullable=False)
    
    user = relationship("User", back_populates="pads")
    backups = relationship("Backup", back_populates="pad", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pad(id='{self.id}', user_id='{self.user_id}')>"
