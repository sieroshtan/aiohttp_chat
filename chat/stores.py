import sqlalchemy as sa

metadata = sa.MetaData()

messages_table = sa.Table('chat_message', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('ts', sa.Unicode(45)),
    sa.Column('text', sa.Unicode(1000)),
    sa.Column('user_sender_id', sa.INTEGER),
    sa.Column('channel_id', sa.INTEGER),
    sa.Column('delivered', sa.BOOLEAN, default=False)
)

user_channel_table = sa.Table('chat_userchannel', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.INTEGER),
    sa.Column('channel_id', sa.INTEGER),
)
