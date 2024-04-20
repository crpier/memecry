"""add user options

Revision ID: 5c13acb87365
Revises: fbcf0920dd16
Create Date: 2024-04-20 01:06:15.735771

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c13acb87365"
down_revision: str | None = "fbcf0920dd16"
branch_labels: str | list[str] | None = None
depends_on: str | list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "desktop_autoplay",
            sa.Boolean(),
            nullable=False,
            server_default=sa.False_(),  # type: ignore
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "mobile_autoplay",
            sa.Boolean(),
            nullable=False,
            server_default=sa.False_(),  # type: ignore
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "mobile_autoplay")
    op.drop_column("users", "desktop_autoplay")
