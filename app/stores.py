import sqlalchemy as sa

metadata = sa.MetaData()

messages_table = sa.Table('chat_message', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('ts', sa.Unicode(45)),
    sa.Column('text', sa.Unicode(1000)),
    sa.Column('user_sender_id', sa.INTEGER),
    sa.Column('channel_id', sa.INTEGER),
    sa.Column('delivered', sa.BOOLEAN, default=False),
    sa.Column('read', sa.BOOLEAN, default=False),
)


user_channel_table = sa.Table('chat_userchannel', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.INTEGER),
    sa.Column('channel_id', sa.INTEGER),
)


user_table = sa.Table('auth_user', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('last_login', sa.Unicode(45)),
    sa.Column('is_superuser', sa.BOOLEAN, default=False),
    sa.Column('password', sa.Unicode(1000)),
    sa.Column('username', sa.Unicode(150)),
    sa.Column('first_name', sa.Unicode(30)),
    sa.Column('last_name', sa.Unicode(30)),
    sa.Column('email', sa.Unicode(250)),
    sa.Column('is_staff', sa.BOOLEAN, default=False),
    sa.Column('is_active', sa.BOOLEAN, default=True),
    sa.Column('date_joined', sa.Unicode(45)),
)

# message_recipient_table = sa.Table('chat_messagerecipient', metadata,
#     sa.Column('id', sa.Integer, primary_key=True),
#     sa.Column('message_id', sa.INTEGER, sa.ForeignKey('chat_message.id')),
#     sa.Column('user_id', sa.INTEGER, sa.ForeignKey('auth_user.id')),
# )
