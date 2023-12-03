"""add score column to posts table

Revision ID: 103e638cc33e
Revises:
Create Date: 2023-12-03 20:18:28.222575

"""

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "103e638cc33e"
down_revision: str | None = None
branch_labels: str | list[str] | None = None
depends_on: str | list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE posts ADD COLUMN score NOT NULL DEFAULT 0")
    op.execute("UPDATE posts SET score = 0")


def downgrade() -> None:
    pass
