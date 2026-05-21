"""add payload to workflows

Revision ID: a3f2b1c9d8e7
Revises: 6674f7b7d247
Create Date: 2026-05-13 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a3f2b1c9d8e7'
down_revision: Union[str, None] = '6674f7b7d247'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('workflows', sa.Column('payload', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('workflows', 'payload')
