"""Create padws schema

Revision ID: 0ed2c80b0270
Revises: 
Create Date: 2025-04-30 03:56:33.469180

"""
from typing import Sequence, Union

from alembic import op

from database.config import DatabaseConfig

# revision identifiers, used by Alembic.
revision: str = '0ed2c80b0270'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(f'CREATE SCHEMA IF NOT EXISTS {DatabaseConfig.APP_SCHEMA_NAME}')
    
def downgrade():
    op.execute(f'DROP SCHEMA IF EXISTS {DatabaseConfig.APP_SCHEMA_NAME} CASCADE')