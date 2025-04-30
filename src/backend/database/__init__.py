"""
Database module for pad.ws application.

This module provides a complete database abstraction layer with:
- Connection management (engine, sessions)
- Data models (UserModel, PadModel, BackupModel)
- Data access (repositories)
- Business logic (services)

Basic usage:
    from src.backend.database import get_db_session, UserService

    async def get_user(user_id: str):
        async for session in get_db_session():
            user_service = UserService(session)
            return await user_service.get_user_by_id(user_id)
"""

# Database connection
from .interface import get_db_session, init_db, engine, async_session

# Configuration
from .config import DatabaseConfig

# Models
from .models import Base, TimestampedBase, UserModel, PadModel, BackupModel

# Repositories
from .repositories import BaseRepository, UserRepository, PadRepository, BackupRepository

# Services
from .services import UserService, PadService, BackupService

__all__ = [
    # Connection
    'get_db_session', 'init_db', 'engine', 'async_session',
    
    # Configuration
    'DatabaseConfig',
    
    # Models
    'Base', 'TimestampedBase', 'UserModel', 'PadModel', 'BackupModel',
    
    # Repositories
    'BaseRepository', 'UserRepository', 'PadRepository', 'BackupRepository',
    
    # Services
    'UserService', 'PadService', 'BackupService',
]
