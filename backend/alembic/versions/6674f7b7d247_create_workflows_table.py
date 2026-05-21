"""create workflows table

Revision ID: 6674f7b7d247
Revises: 
Create Date: 2026-05-12 19:39:17.945184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identifiants de révision utilisés par Alembic.
revision: str = '6674f7b7d247'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commandes auto-générées par Alembic - à ajuster si nécessaire ###
    op.create_table('workflows',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('thread_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('approval_status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_thread_id'), 'workflows', ['thread_id'], unique=True)
    # ### fin des commandes Alembic ###


def downgrade() -> None:
    # ### commandes auto-générées par Alembic - à ajuster si nécessaire ###
    op.drop_index(op.f('ix_workflows_thread_id'), table_name='workflows')
    op.drop_table('workflows')
    # ### fin des commandes Alembic ###
