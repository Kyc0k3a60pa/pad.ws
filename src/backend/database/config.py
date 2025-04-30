"""
Database configuration settings for the pad.ws application.

This module contains configuration constants and helper methods
for database-related operations.
"""

class DatabaseConfig:
    """Database configuration settings.
    
    These settings control various aspects of database behavior,
    particularly related to schema and backup management.
    
    Attributes:
        BACKUP_INTERVAL_SECONDS: Time between automatic backups in seconds.
        MAX_BACKUPS_PER_USER: Maximum number of backups to keep per user.
        APP_SCHEMA_NAME: The PostgreSQL schema name for application tables.
    """
    
    # Canvas backup configuration
    BACKUP_INTERVAL_SECONDS = 300  # 5 minutes between backups
    MAX_BACKUPS_PER_USER = 10  # Maximum number of backups to keep per user
    APP_SCHEMA_NAME = "pad_ws"
    
    @classmethod
    def get_schema_name(cls) -> str:
        """Get the application schema name.
        
        Returns:
            str: The configured schema name for application tables.
        """
        return cls.APP_SCHEMA_NAME
    
    @classmethod
    def get_table_full_name(cls, table_name: str) -> str:
        """Get the fully qualified table name including schema.
        
        Args:
            table_name: The base table name without schema.
            
        Returns:
            str: The fully qualified table name (schema.table_name).
        """
        return f"{cls.APP_SCHEMA_NAME}.{table_name}"
