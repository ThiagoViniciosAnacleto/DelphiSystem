"""adiciona criado_por_id em chamados

Revision ID: e8f9a1b2c3d4
Revises: 6834b16ed755
Create Date: 2026-08-21 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e8f9a1b2c3d4'
down_revision: Union[str, None] = '6834b16ed755'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('chamados', schema=None) as batch_op:
        batch_op.add_column(sa.Column('criado_por_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_chamados_criado_por_id_usuarios',
            'usuarios',
            ['criado_por_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_index(
            'ix_chamados_criado_por_id',
            ['criado_por_id'],
            unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table('chamados', schema=None) as batch_op:
        batch_op.drop_index('ix_chamados_criado_por_id')
        batch_op.drop_constraint('fk_chamados_criado_por_id_usuarios', type_='foreignkey')
        batch_op.drop_column('criado_por_id')
