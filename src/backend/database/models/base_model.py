from uuid import uuid4

from sqlalchemy import Column, DateTime, UUID, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()

class TimestampedBase(Base):
    """Abstract base class that includes timestamp columns"""
    __abstract__ = True  # This prevents SQLAlchemy from creating a table for this class
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
