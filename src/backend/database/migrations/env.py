import os
import sys
from pathlib import Path
from urllib.parse import quote_plus as urlquote
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import create_engine, text

# Add the database directory to the Python path
database_dir = Path(__file__).parent.parent
sys.path.insert(0, str(database_dir))

# Import from the models package
from models.base_model import Base
from models.user_model import User
from models.pad_model import Pad
from models.backup_model import Backup

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

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_url)
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="padws"
        )
        
        with context.begin_transaction():
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS padws"))
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
