"""aggiunge data_consegna a ordine

Revision ID: 14950a2776b7
Revises: 9ffaa9fd4479
Create Date: 2026-07-07 21:28:18.170214
"""

from alembic import op
import sqlalchemy as sa
from datetime import date


# revision identifiers, used by Alembic.
revision = '14950a2776b7'
down_revision = '9ffaa9fd4479'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'data_consegna',
                sa.Date(),
                nullable=False,
                server_default=sa.text(f"'{date.today().isoformat()}'")
            )
        )

    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.alter_column('data_consegna', server_default=None)


def downgrade():
    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.drop_column('data_consegna')
