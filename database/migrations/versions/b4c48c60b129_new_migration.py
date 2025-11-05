"""New migration

Revision ID: b4c48c60b129
Revises: de9f1d4f20c9
Create Date: 2025-10-20 18:06:33.574619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c48c60b129'
down_revision: Union[str, None] = 'de9f1d4f20c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
