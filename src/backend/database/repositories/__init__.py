"""
Database repositories for the pad.ws application.

This module exports all the repository classes used for data access:
- BaseRepository: Generic base repository with common CRUD operations
- UserRepository: Repository for user-related database operations
- PadRepository: Repository for pad-related database operations
- BackupRepository: Repository for backup-related database operations

Repositories handle direct database access and provide a clean API
for performing operations on the database entities.
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .pad_repository import PadRepository
from .backup_repository import BackupRepository

__all__ = ['BaseRepository', 'UserRepository', 'PadRepository', 'BackupRepository']
