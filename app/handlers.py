import json
import time
import aiohttp
from aiohttp import web
from sqlalchemy import select
from stores import messages_table, user_channel_table, user_table


# from stores import messages_table, message_recipient_table


async def websocket_handler(request):
    nc = request.app['nats']
    db = request.app['db']

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    current_user_id = request.GET['user']

    async def user_handler(event):
        event_data = json.loads(event.data.decode('utf-8'))
        ws.send_str(json.dumps(event_data))

    sid_user = await nc.subscribe('channel.%s' % current_user_id, cb=user_handler)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                event_data = json.loads(msg.data)

                if event_data['type'] == 'message.im':
                    ts = time.time()
                    channel_id = event_data['channel']
                    to_id = event_data['to']

                    async with db.acquire() as conn:
                        res = await conn.execute(
                            messages_table.insert().values(ts=ts,
                                                           text=event_data['text'],
                                                           user_sender_id=current_user_id,
                                                           channel_id=channel_id,
                                                           delivered=False,
                                                           read=False))

                        current_user_name = await conn.execute(
                            select([user_table.c.username]).where(user_table.c.id == current_user_id)
                        )
                        # await conn.execute(
                        #     message_recipient_table.insert().values(message_id=msg_id, user_id=to_id))

                    event_data['ts'] = ts
                    event_data['user_id'] = current_user_id
                    event_data['user_name'] = list(current_user_name)[0][0]
                    event_data['msg_id'] = list(res)[0][0]
                    del event_data['to']

                    await nc.publish('channel.%s' % to_id, json.dumps(event_data).encode('utf-8'))
                    await nc.publish('channel.%s' % current_user_id, json.dumps(event_data).encode('utf-8'))
                    # await nc.publish('channel.%s' % current_user_id, msg.data.encode('utf-8'))

                elif event_data['type'] == 'message.group':
                    ts = time.time()
                    channel_id = event_data['channel']

                    async with db.acquire() as conn:
                        res = await conn.execute(
                            messages_table.insert().values(ts=ts,
                                                           text=event_data['text'],
                                                           user_sender_id=current_user_id,
                                                           channel_id=event_data['channel'],
                                                           delivered=False,
                                                           read=False))

                        channel_users = await conn.execute(
                            select([user_channel_table.c.user_id]).where(user_channel_table.c.channel_id == channel_id)
                        )
                        current_user_name = await conn.execute(
                            select([user_table.c.username]).where(user_table.c.id == current_user_id)
                        )

                    event_data['ts'] = ts
                    event_data['user_id'] = current_user_id
                    event_data['user_name'] = list(current_user_name)[0][0]
                    event_data['msg_id'] = list(res)[0][0]

                    # for user in list(channel_users):
                    #     id_user = user[0]
                    #     await nc.publish('channel.%s' % id_user, json.dumps(event_data).encode('utf-8'))
                    for row in channel_users:
                        to_id = row[user_channel_table.c.user_id]
                        await nc.publish('channel.%s' % to_id, json.dumps(event_data).encode('utf-8'))

                elif event_data['type'] == 'message.read':
                    channel_id = event_data['channel']
                    last_msg_id = event_data['msg_id']

                    async with db.acquire() as conn:
                        # messages = await conn.execute(
                        #     select([messages_table]).where(messages_table.c.channel_id == channel_id).where(messages_table.c.user_sender_id != current_user_id)
                        # )
                        r = await conn.execute(
                            messages_table.update().where(messages_table.c.channel_id == channel_id).where(
                                messages_table.c.user_sender_id != current_user_id).where(
                                messages_table.c.read == False).where(messages_table.c.id <= last_msg_id).values(
                                read=True).returning(messages_table.c.id))

                    event_data['msg_list'] = list(msg[0] for msg in list(r))

                    await nc.publish('channel.%s' % current_user_id, json.dumps(event_data).encode('utf-8'))

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
    finally:
        await nc.unsubscribe(sid_user)
        print('websocket connection closed')

    return ws
