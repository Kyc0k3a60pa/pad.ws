"""Migrate data from old tables to padws schema

Revision ID: cb2356d681f9
Revises: 46c1edc1a40a
Create Date: 2025-04-30 04:23:44.170878

"""

import json
from typing import Sequence, Union
from uuid import uuid4

from sqlalchemy import text
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'cb2356d681f9'
down_revision: Union[str, None] = '46c1edc1a40a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Get connection
    connection = op.get_bind()
    
    # 1. Migrate users (create a user for each unique user_id in canvas_data)
    canvas_users = connection.execute(text("SELECT user_id FROM canvas_data")).fetchall()
    
    for user_row in canvas_users:
        jwt_token_id = user_row[0]
        migration_email = f"migration_required"
        
        # Insert into new users table
        connection.execute(
            text("INSERT INTO padws.users (id, username, email, jwt_token_id, created_at, updated_at) VALUES (:id, :username, :email, :jwt_token_id, NOW(), NOW())"),
            {"id": str(uuid4()), "username": None, "email": migration_email, "jwt_token_id": jwt_token_id}
        )
        
        # Get the inserted user's ID
        new_user_id = connection.execute(
            text("SELECT id FROM padws.users WHERE jwt_token_id = :jwt_token_id"),
            {"jwt_token_id": jwt_token_id}

        ).scalar()
        
        # 2. Migrate pad data
        canvas_data = connection.execute(
            text("SELECT data, updated_at FROM canvas_data WHERE user_id = :user_id"),
            {"user_id": jwt_token_id}
        ).fetchone()
        
        if canvas_data:
            pad_data = canvas_data[0]
            updated_at = canvas_data[1]
            
            # Insert into new pads table
            connection.execute(
                text("INSERT INTO padws.pads (id, user_id, data, created_at, updated_at) VALUES (:id, :user_id, :data, :created_at, :updated_at)"),
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
                text("SELECT id FROM padws.pads WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                {"user_id": new_user_id}
            ).scalar()
            
            # 3. Migrate backups
            backups = connection.execute(
                text("SELECT canvas_data, timestamp FROM canvas_backups WHERE user_id = :user_id ORDER BY timestamp"),
                {"user_id": jwt_token_id}
            ).fetchall()
            
            for backup in backups:
                backup_data = backup[0]
                timestamp = backup[1]
                
                # Insert into new backups table
                connection.execute(
                    text("INSERT INTO padws.backups (id, pad_id, data, created_at, updated_at) VALUES (:id, :pad_id, :data, :created_at, :updated_at)"),
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
    connection.execute(text("DROP SCHEMA padws CASCADE"))
    connection.execute(text("CREATE SCHEMA padws"))

