"""Add avatar_image to User model

Revision ID: b90805a30d84
Revises: 9ed16168f61f
Create Date: 2025-06-12 13:58:11.915646

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b90805a30d84'
down_revision = '9ed16168f61f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('borrow_record', schema=None) as batch_op:
        batch_op.alter_column('borrow_date',
               existing_type=mysql.DATETIME(),
               comment='实际借出日期',
               existing_comment='实际借出日期(管理员批准后填写)',
               existing_nullable=True)
        batch_op.alter_column('due_date',
               existing_type=mysql.DATETIME(),
               comment='应还日期',
               existing_comment='应还日期(管理员批准后计算)',
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.SMALLINT(),
               comment='状态',
               existing_comment='状态:0-借阅待批,1-借阅中,2-已归还,3-逾期归还,6-还书待批,9-借阅失败',
               existing_nullable=False)

    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.SMALLINT(),
               comment='预约状态',
               existing_comment='预约状态: 1-等待中, 2-已满足, 3-已取消/过期',
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_image', sa.String(length=255), nullable=True, comment='用户头像图片路径'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('avatar_image')

    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.SMALLINT(),
               comment='预约状态: 1-等待中, 2-已满足, 3-已取消/过期',
               existing_comment='预约状态',
               existing_nullable=False)

    with op.batch_alter_table('borrow_record', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.SMALLINT(),
               comment='状态:0-借阅待批,1-借阅中,2-已归还,3-逾期归还,6-还书待批,9-借阅失败',
               existing_comment='状态',
               existing_nullable=False)
        batch_op.alter_column('due_date',
               existing_type=mysql.DATETIME(),
               comment='应还日期(管理员批准后计算)',
               existing_comment='应还日期',
               existing_nullable=True)
        batch_op.alter_column('borrow_date',
               existing_type=mysql.DATETIME(),
               comment='实际借出日期(管理员批准后填写)',
               existing_comment='实际借出日期',
               existing_nullable=True)

    # ### end Alembic commands ###
