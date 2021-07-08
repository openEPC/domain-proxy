"""empty message

Revision ID: 9fb9db0b2bcc
Revises: 4a706d0adc45
Create Date: 2021-06-21 10:51:50.763296

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '9fb9db0b2bcc'
down_revision = '4a706d0adc45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('grant_state',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('grant',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('state_id', sa.Integer(), nullable=True),
                    sa.Column('cbsd_id', sa.String(), nullable=False),
                    sa.Column('grant_id', sa.String(), nullable=False),
                    sa.Column('grant_expire_time', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('transmit_expire_time', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('heartbeat_interval', sa.Integer(), nullable=True),
                    sa.Column('channel_type', sa.String(), nullable=True),
                    sa.Column('created_date', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_date', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(['state_id'], ['grant_state.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('request', sa.Column('created_date', sa.DateTime(
        timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('request', sa.Column('updated_date', sa.DateTime(
        timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('response', sa.Column('grant_id', sa.Integer(), nullable=True))
    op.add_column('response', sa.Column('created_date', sa.DateTime(
        timezone=True), server_default=sa.text('now()'), nullable=False))
    op.create_foreign_key(None, 'response', 'grant', ['grant_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'response', type_='foreignkey')
    op.drop_column('response', 'created_date')
    op.drop_column('response', 'grant_id')
    op.drop_column('request', 'updated_date')
    op.drop_column('request', 'created_date')
    op.drop_table('grant')
    op.drop_table('grant_state')
    # ### end Alembic commands ###