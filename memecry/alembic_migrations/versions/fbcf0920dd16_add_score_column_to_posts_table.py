"""add score column to posts table

Revision ID: fbcf0920dd16
Revises:
Create Date: 2023-12-03 21:48:59.355540

"""

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fbcf0920dd16"
down_revision: str | None = "9af368c9ecdc"
branch_labels: str | list[str] | None = None
depends_on: str | list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE posts ADD COLUMN score NOT NULL DEFAULT 0")
    op.execute("UPDATE posts SET score = 0")


def downgrade() -> None:
    pass
