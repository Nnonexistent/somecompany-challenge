"""add_user

Revision ID: 7e004ac152bc
Revises: 4b99c04fa336
Create Date: 2023-03-16 02:41:32.872075
"""
import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision = '7e004ac152bc'
down_revision = '4b99c04fa336'
branch_labels = None
depends_on = None


# Create an ad-hoc table to use for the insert statement.
users_table = table(
    'user',
    column('id', Uuid),
    column('name', String),
    column('hashed_password', String),
)


def upgrade() -> None:
    op.bulk_insert(
        users_table,
        [
            {
                'id': uuid.uuid4().hex,
                'name': 'user',
                'hashed_password': '$2b$12$RzgPCdG1CEx1ZEK6dSEEMeY4xl6/Oz.ODlbDiXJPZs5uU68ouiNO2',  # qwe123
            },
        ],
    )


def downgrade() -> None:
    pass
