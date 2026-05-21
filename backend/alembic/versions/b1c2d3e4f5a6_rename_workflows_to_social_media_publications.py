"""rename workflows to social_media_publications

Revision ID: b1c2d3e4f5a6
Revises: a3f2b1c9d8e7
Create Date: 2026-05-13

Clarification architecturale : la table `workflows` représente une projection
métier (lifecycle de publication), pas le runtime LangGraph (MemorySaver).
Ce renommage aligne la persistence sur l'ubiquitous language DDD avant
l'introduction des checkpointers durables (étape 20).
"""
from alembic import op

revision = "b1c2d3e4f5a6"
down_revision = "a3f2b1c9d8e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("workflows", "social_media_publications")


def downgrade() -> None:
    op.rename_table("social_media_publications", "workflows")
