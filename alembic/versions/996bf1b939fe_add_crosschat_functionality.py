"""Add crosschat functionality

Revision ID: 996bf1b939fe
Revises: e412b029eee9
Create Date: 2024-02-15 20:43:14.959158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '996bf1b939fe'
down_revision = 'e412b029eee9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('CrosschatChannels',
    sa.Column('TargetChannelId', sa.BigInteger(), nullable=True),
    sa.Column('TargetGuildId', sa.BigInteger(), nullable=True),
    sa.Column('DiscordId', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('DiscordId')
    )
    op.create_table('CrosschatAssociations',
    sa.Column('guild_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['CrosschatChannels.DiscordId'], ),
    sa.ForeignKeyConstraint(['guild_id'], ['Guilds.DiscordId'], ),
    sa.PrimaryKeyConstraint('guild_id', 'channel_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('CrosschatAssociations')
    op.drop_table('CrosschatChannels')
    # ### end Alembic commands ###
