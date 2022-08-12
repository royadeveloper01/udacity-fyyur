"""empty message

Revision ID: d5b408e6c4d9
Revises: dc0bd0bd2bf7
Create Date: 2022-08-11 21:13:27.901596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5b408e6c4d9'
down_revision = 'dc0bd0bd2bf7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('venues', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'seeking_description')
    op.drop_column('venues', 'seeking_talent')
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
