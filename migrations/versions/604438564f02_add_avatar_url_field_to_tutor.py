"""Add avatar_url field to tutor.

Revision ID: 604438564f02
Revises: 3a0a3b54cd34
Create Date: 2023-07-28 14:14:17.590411

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '604438564f02'
down_revision = '3a0a3b54cd34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tutor', sa.Column('avatar_url', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tutor', 'avatar_url')
    # ### end Alembic commands ###
