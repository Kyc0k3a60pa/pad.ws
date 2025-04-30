"""Create new tables in padws schema

Revision ID: 46c1edc1a40a
Revises: 0ed2c80b0270
Create Date: 2025-04-30 04:17:03.786360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from database.config import DatabaseConfig

# revision identifiers, used by Alembic.
revision: str = '46c1edc1a40a'
down_revision: Union[str, None] = '0ed2c80b0270'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

schema_name = DatabaseConfig.get_schema_name()

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('username', sa.String(), nullable=True, unique=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('jwt_id', sa.String(), nullable=True, unique=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username'),
    schema=schema_name
    )
    op.create_table('pads',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['padws.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema=schema_name
    )
    op.create_table('backups',
    sa.Column('pad_id', sa.UUID(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['pad_id'], ['padws.pads.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema=schema_name
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('backups', schema=schema_name)
    op.drop_table('pads', schema=schema_name)
    op.drop_table('users', schema=schema_name)
