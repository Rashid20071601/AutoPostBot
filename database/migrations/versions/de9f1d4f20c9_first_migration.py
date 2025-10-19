"""First migration

Revision ID: de9f1d4f20c9
Revises: c57b2b07a1c6
Create Date: 2025-10-19 13:34:46.321722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de9f1d4f20c9'
down_revision: Union[str, None] = 'c57b2b07a1c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
