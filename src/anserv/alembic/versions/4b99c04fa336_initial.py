"""Initial

Revision ID: 4b99c04fa336
Revises:
Create Date: 2023-03-16 02:40:22.889206

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '4b99c04fa336'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('entry',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('dt', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('date_start', sa.Date(), nullable=False),
    sa.Column('date_end', sa.Date(), nullable=False),
    sa.Column('merge_time_min', sa.Integer(), nullable=False),
    sa.Column('merge_time_max', sa.Integer(), nullable=False),
    sa.Column('merge_time_mean', sa.Float(), nullable=False),
    sa.Column('merge_time_median', sa.Float(), nullable=False),
    sa.Column('merge_time_quantile_10', sa.Float(), nullable=False),
    sa.Column('merge_time_quantile_90', sa.Float(), nullable=False),
    sa.Column('merge_time_mode', sa.Integer(), nullable=False),
    sa.Column('merge_time_std', sa.Float(), nullable=False),
    sa.Column('review_time_min', sa.Integer(), nullable=False),
    sa.Column('review_time_max', sa.Integer(), nullable=False),
    sa.Column('review_time_mean', sa.Float(), nullable=False),
    sa.Column('review_time_median', sa.Float(), nullable=False),
    sa.Column('review_time_quantile_10', sa.Float(), nullable=False),
    sa.Column('review_time_quantile_90', sa.Float(), nullable=False),
    sa.Column('review_time_mode', sa.Integer(), nullable=False),
    sa.Column('review_time_std', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('atom',
    sa.Column('entry_id', sa.Uuid(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('team', sa.String(), nullable=False),
    sa.Column('review_time', sa.Integer(), nullable=False),
    sa.Column('merge_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['entry_id'], ['entry.id'], ),
    sa.PrimaryKeyConstraint('entry_id', 'date', 'team')
    )
    op.create_table('visualization',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('entry_id', sa.Uuid(), nullable=False),
    sa.Column('dt', sa.DateTime(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),  # type: ignore[no-untyped-call]
    sa.ForeignKeyConstraint(['entry_id'], ['entry.id'], ),
    sa.PrimaryKeyConstraint('id', 'entry_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visualization')
    op.drop_table('atom')
    op.drop_table('entry')
    op.drop_table('user')
    # ### end Alembic commands ###
