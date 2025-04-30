"""
Database interface module for pad.ws application.

This module provides the core database connection functionality,
including engine setup, session management, and database initialization.

Environment variables:
    POSTGRES_USER: PostgreSQL username (default: postgres)
    POSTGRES_PASSWORD: PostgreSQL password (default: postgres)
    POSTGRES_DB: PostgreSQL database name (default: pad)
    POSTGRES_HOST: PostgreSQL host (default: localhost)
    POSTGRES_PORT: PostgreSQL port (default: 5432)
"""

import os
from typing import AsyncGenerator
from urllib.parse import quote_plus as urlquote

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from .config import DatabaseConfig

# Load environment variables
load_dotenv()

# PostgreSQL connection configuration
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'pad')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# SQLAlchemy async database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{urlquote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session.
    
    This function provides a context-managed database session that
    automatically handles commits, rollbacks, and cleanup.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
        
    Example:
        ```python
        async for session in get_db_session():
            result = await session.execute(query)
            # No need to commit - it's handled automatically
        ```
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize the database with required tables and schema.
    
    This function:
    1. Creates the application schema if it doesn't exist
    2. Creates all tables defined in the models
    
    Should be called once at application startup.
    """
    # Import here to avoid circular imports
    from .models.base_model import Base
    
    async with engine.begin() as conn:
        # Create schema if it doesn't exist
        schema_name = DatabaseConfig.get_schema_name()
        try:
            await conn.execute(CreateSchema(schema_name, if_not_exists=True))
            print(f"Created '{schema_name}' schema or it already exists")
        except Exception as e:
            print(f"Error creating schema: {e}")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Created all tables")
