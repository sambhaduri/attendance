"""Create table

Revision ID: 149d90429101
Revises: 580cb50cbf15
Create Date: 2025-04-02 17:01:20.683792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '149d90429101'
down_revision = '580cb50cbf15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))

    with op.batch_alter_table('breaks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('breaks', schema=None) as batch_op:
        batch_op.drop_column('name')

    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###
