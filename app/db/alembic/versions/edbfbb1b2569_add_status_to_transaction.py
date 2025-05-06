"""Add status to transaction

Revision ID: edbfbb1b2569
Revises: 13b540cb2b7f
Create Date: 2025-05-06 16:09:51.265034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'edbfbb1b2569'
down_revision: Union[str, None] = '13b540cb2b7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transaction_status_enum = postgresql.ENUM('NEW', 'PENDING', 'PROCESSED', 'FAIL', name='transactionstatus')


def upgrade() -> None:
    """Upgrade schema."""
    transaction_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'transactions',
        sa.Column('status', transaction_status_enum, nullable=False, server_default='NEW')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'status')
    transaction_status_enum.drop(op.get_bind(), checkfirst=True)
