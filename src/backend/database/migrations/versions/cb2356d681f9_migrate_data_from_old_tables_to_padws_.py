"""Migrate data from old tables to app schema

Revision ID: cb2356d681f9
Revises: 46c1edc1a40a
Create Date: 2025-04-30 04:23:44.170878

"""

import json
from typing import Sequence, Union
from uuid import uuid4

from sqlalchemy import text
from alembic import op

from database.config import DatabaseConfig

# revision identifiers, used by Alembic.
revision: str = 'cb2356d681f9'
down_revision: Union[str, None] = '46c1edc1a40a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

schema_name = DatabaseConfig.get_schema_name()
def upgrade():
    # Get connection
    connection = op.get_bind()

    # 1. Migrate users (create a user for each unique user_id in canvas_data)
    canvas_users = connection.execute(text(f"SELECT user_id FROM canvas_data")).fetchall()
    
    for user_row in canvas_users:
        jwt_id = user_row[0]
        migration_email = f"migration_required"
        
        # Insert into new users table
        connection.execute(
            text(f"INSERT INTO {schema_name}.users (id, username, email, jwt_id, created_at, updated_at) VALUES (:id, :username, :email, :jwt_id, NOW(), NOW())"),
            {"id": str(uuid4()), "username": None, "email": migration_email, "jwt_id": jwt_id}
        )
        
        # Get the inserted user's ID
        new_user_id = connection.execute(
            text(f"SELECT id FROM {schema_name}.users WHERE jwt_id = :jwt_id"),
            {"jwt_id": jwt_id}

        ).scalar()
        
        # 2. Migrate pad data
        canvas_data = connection.execute(
            text(f"SELECT data, updated_at FROM canvas_data WHERE user_id = :user_id"),
            {"user_id": jwt_id}
        ).fetchone()
        
        if canvas_data:
            pad_data = canvas_data[0]
            updated_at = canvas_data[1]
            
            # Insert into new pads table
            connection.execute(
                text(f"INSERT INTO {schema_name}.pads (id, user_id, data, created_at, updated_at) VALUES (:id, :user_id, :data, :created_at, :updated_at)"),
                {
                    "id": str(uuid4()),
                    "user_id": new_user_id,
                    "data": json.dumps(pad_data),
                    "created_at": updated_at,
                    "updated_at": updated_at
                }
            )
            
            # Get the inserted pad's ID
            new_pad_id = connection.execute(
                text(f"SELECT id FROM {schema_name}.pads WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                {"user_id": new_user_id}
            ).scalar()
            
            # 3. Migrate backups
            backups = connection.execute(
                text(f"SELECT canvas_data, timestamp FROM canvas_backups WHERE user_id = :user_id ORDER BY timestamp"),
                {"user_id": jwt_id}
            ).fetchall()
            
            for backup in backups:
                backup_data = backup[0]
                timestamp = backup[1]
                
                # Insert into new backups table
                connection.execute(
                    text(f"INSERT INTO {schema_name}.backups (id, pad_id, data, created_at, updated_at) VALUES (:id, :pad_id, :data, :created_at, :updated_at)"),
                    {
                        "id": str(uuid4()),
                        "pad_id": new_pad_id,
                        "data": json.dumps(backup_data),
                        "created_at": timestamp,
                        "updated_at": timestamp
                    }
                )

def downgrade():
    connection = op.get_bind()
    connection.execute(text(f"DROP SCHEMA {schema_name} CASCADE"))
    connection.execute(text(f"CREATE SCHEMA {schema_name}"))

