"""Aggiunge confezioni e descrizione prodotto

Revision ID: d6bcfd968dc8
Revises:
Create Date: 2026-07-07 16:44:20.974160
"""

from alembic import op
import sqlalchemy as sa

revision = 'd6bcfd968dc8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('riga_ordine', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confezione_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('quantita_magazzino', sa.Float(), nullable=True))
        batch_op.create_foreign_key('fk_riga_ordine_confezione_id', 'confezione', ['confezione_id'], ['id'])


def downgrade():
    with op.batch_alter_table('riga_ordine', schema=None) as batch_op:
        batch_op.drop_constraint('fk_riga_ordine_confezione_id', type_='foreignkey')
        batch_op.drop_column('quantita_magazzino')
        batch_op.drop_column('confezione_id')
