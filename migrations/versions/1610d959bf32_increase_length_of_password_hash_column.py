"""Increase length of password_hash column

Revision ID: 1610d959bf32
Revises: 2530c35020b5
Create Date: 2025-06-09 20:39:08.518808

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1610d959bf32'
down_revision = '2530c35020b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128),
               type_=sa.String(length=256),
               existing_comment='加密密码',
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=256),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128),
               existing_comment='加密密码',
               existing_nullable=False)

    # ### end Alembic commands ###
