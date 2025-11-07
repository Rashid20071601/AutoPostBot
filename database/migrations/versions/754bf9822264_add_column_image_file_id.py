"""Add column 'image_file_id'

Revision ID: 754bf9822264
Revises: b4c48c60b129
Create Date: 2025-11-05 20:22:46.081766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '754bf9822264'
down_revision: Union[str, None] = 'b4c48c60b129'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
