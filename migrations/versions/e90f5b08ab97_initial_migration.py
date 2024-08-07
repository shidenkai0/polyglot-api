"""Initial migration

Revision ID: e90f5b08ab97
Revises:
Create Date: 2023-06-13 16:37:15.879783

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'e90f5b08ab97'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'user',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
    )
    op.create_index(op.f('user_email_idx'), 'user', ['email'], unique=True)
    op.create_table(
        'oauth_account',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('user_id', UUID, nullable=False),
        sa.Column('oauth_name', sa.String(length=100), nullable=False),
        sa.Column('access_token', sa.String(length=1024), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('refresh_token', sa.String(length=1024), nullable=True),
        sa.Column('account_id', sa.String(length=320), nullable=False),
        sa.Column('account_email', sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('oauth_account_user_id_fkey'), ondelete='cascade'),
    )
    op.create_index(op.f('oauth_account_account_id_idx'), 'oauth_account', ['account_id'], unique=False)
    op.create_index(op.f('oauth_account_oauth_name_idx'), 'oauth_account', ['oauth_name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('oauth_account_oauth_name_idx'), table_name='oauth_account')
    op.drop_index(op.f('oauth_account_account_id_idx'), table_name='oauth_account')
    op.drop_table('oauth_account')
    op.drop_index(op.f('user_email_idx'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
