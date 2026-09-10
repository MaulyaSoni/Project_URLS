"""IP init and Unique Constraint in URLStats table

Revision ID: 2ada7a08929c
Revises: 3daa6949fff2, b862f64f3601
Create Date: 2026-09-09 10:01:34.317263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ada7a08929c'
down_revision: Union[str, Sequence[str], None] = ('3daa6949fff2', 'b862f64f3601')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
