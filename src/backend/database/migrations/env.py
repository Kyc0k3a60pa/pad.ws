import os
import sys
from pathlib import Path
from urllib.parse import quote_plus as urlquote
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import create_engine, text

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent  # Navigate to backend/
sys.path.insert(0, str(backend_dir))

# Import from the models package
from database.models.base_model import Base
from database.models.user_model import UserModel
from database.models.pad_model import PadModel
from database.models.backup_model import BackupModel
from database.config import DatabaseConfig
# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'pad')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# Construct database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{urlquote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# This is the Alembic Config object
config = context.config

# Set target metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

sync_url = DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')

schema_name = DatabaseConfig.get_schema_name()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_url)
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=schema_name
        )
        
        with context.begin_transaction():
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            context.run_migrations()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
