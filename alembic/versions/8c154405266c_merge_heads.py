"""merge heads

Revision ID: 8c154405266c
Revises: 09a62e3cfb52, 2da20a21ce10, 3daa6949fff2
Create Date: 2026-09-29 11:33:14.624242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c154405266c'
down_revision: Union[str, Sequence[str], None] = ('09a62e3cfb52', '2da20a21ce10', '3daa6949fff2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
