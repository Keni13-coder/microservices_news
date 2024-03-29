"""Database creation

Revision ID: 8048e80e04e1
Revises: 
Create Date: 2024-01-14 18:36:48.930936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision: str = '8048e80e04e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('uid', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('create_date', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=255), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_uid'), 'user', ['uid'], unique=False)
    op.create_table('token',
    sa.Column('uid', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('token', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('expires', sa.DateTime(), nullable=False),
    sa.Column('user_uid', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['user_uid'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_token_token'), 'token', ['token'], unique=True)
    op.create_index(op.f('ix_token_uid'), 'token', ['uid'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_token_uid'), table_name='token')
    op.drop_index(op.f('ix_token_token'), table_name='token')
    op.drop_table('token')
    op.drop_index(op.f('ix_user_uid'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
