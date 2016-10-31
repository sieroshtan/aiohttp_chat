import sqlalchemy as sa

metadata = sa.MetaData()

messages_table = sa.Table('chat_message', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('ts', sa.Unicode(45)),
    sa.Column('text', sa.Unicode(1000)),
    sa.Column('user_id', sa.INTEGER),
    sa.Column('delivered', sa.BOOLEAN, default=False),
    sa.Column('read', sa.BOOLEAN, default=False),
)


message_recipient_table = sa.Table('chat_messagerecipient', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('message_id', sa.INTEGER, sa.ForeignKey('chat_message.id')),
    sa.Column('user_id', sa.INTEGER, sa.ForeignKey('auth_user.id')),
)
