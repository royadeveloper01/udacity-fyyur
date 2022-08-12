"""empty message

Revision ID: 19b617fdee74
Revises: 0779d595cd95
Create Date: 2022-08-12 01:55:39.914697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19b617fdee74'
down_revision = '0779d595cd95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website_link')
    # ### end Alembic commands ###