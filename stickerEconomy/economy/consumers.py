from channels.auth import channel_session_user_from_http, channel_session_user
from django.shortcuts import get_object_or_404
from .models import Room,Message, TradeRequest
import json
from channels import Channel
from .utils import catch_client_error, get_room_or_error, trade_stickers
from django.conf import settings
from .exceptions import ClientError


MODIFIED_MESSAGE = "A trade has been Modified"
DECLINED_MESSAGE = "A trade has been Declined"
CONFIRMED_MESSAGE = "A trade has been Confirmed"
COMPELTED_MESSAGE = "A trade has been Completed"


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    message.channel_session['rooms'] = []
    web = list(message.user.room_set.all())
    for room in web:
        if(room.active):
            room.websocket_group.add(message.reply_channel)
            # message.channel_session['rooms'].append(l.websocket_group)
            message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
        print(message.channel_session['rooms'])

@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    for room_id in message.channel_session.get("rooms", set()):
        try:
            room = Room.objects.get(pk=room_id)
            # Removes us from the room's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            room.websocket_group.discard(message.reply_channel)
        except Room.DoesNotExist:
            pass


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)

# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
@catch_client_error
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!

    print("JOIN")
    print(message.user)
    room = get_room_or_error(message["room"], message.user)


    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the chat room gets them.
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
    # Send a message back that will prompt them to open the room
    # Done server-side so that we could, for example, make people
    # join rooms automatically.
    messages = list(room.message_set.order_by('created_date').values('message', 'sender__username','msg_type'))
    other_user=room.users.exclude(pk=message.user.pk).get()
    trade_requests = list(TradeRequest.objects.filter(accepted=True, users=other_user.pk).filter(users=message.user.pk).values('pk','requested_sticker__title','given_sticker__title','requested_sticker__image','requested_sticker__quantity','given_sticker__image', 'given_sticker__quantity','requested_quantity','given_quantity','given_completed','requested_completed', 'given_sticker__owner'))

    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": other_user.username,
            "messages":messages,
            "client": message.user.pk,
            "trade_requests": trade_requests,
        }),
    })

@channel_session_user
@catch_client_error
def chat_leave(message):
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)

    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
    # Send a message back that will prompt them to close the room
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })

@channel_session_user
@catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    msg = Message.objects.create(message=message["message"], room=room, sender=message.user)
    room.send_message(msg)

@channel_session_user
def trade_confirm(message):
    trade = get_object_or_404(TradeRequest, pk=int(message['trade']))
    room = get_room_or_error(message["room"], message.user)

    if message.user == trade.given_sticker.owner and trade.requested_completed == True or message.user == trade.requested_sticker.owner and trade.given_completed == True:
        pk = trade.pk
        trade_stickers(trade)
        room.active = False
        room.save()
        room.websocket_group.send({
            "text": json.dumps({
                "traded": pk,
            }),
        })
        msg = Message.objects.create(message=COMPELTED_MESSAGE, room=room, sender=message.user, msg_type=2)
        room.send_message(msg)
    elif message.user == trade.given_sticker.owner:
        trade.given_completed = True
        trade.save()
        room.websocket_group.send({
            "text": json.dumps({
                "traded": trade.pk,
                "user": message.user.pk,
                "username": message.user.username,
            }),
        })
        msg = Message.objects.create(message=CONFIRMED_MESSAGE, room=room, sender=message.user, msg_type=2)
        room.send_message(msg)
    elif message.user == trade.requested_sticker.owner:
        trade.requested_completed = True
        trade.save()
        room.websocket_group.send({
            "text": json.dumps({
                "traded": trade.pk,
                "user": message.user.pk,
                "username": message.user.username,
            }),
        })
        msg = Message.objects.create(message=CONFIRMED_MESSAGE, room=room, sender=message.user, msg_type=2)
        room.send_message(msg)
    else:
        print("Error")   

@channel_session_user
def trade_modify(message):
    trade = get_object_or_404(TradeRequest, pk=int(message['trade']))
    room = get_room_or_error(message["room"], message.user)
    trade.requested_quantity = message['requested_quantity']
    trade.given_quantity = message['given_quantity']
    trade.given_completed = False
    trade.requested_completed = False
    trade.save()
    room.websocket_group.send({
        "text": json.dumps({
            "modified": trade.pk,
            "requested_quantity": trade.requested_quantity,
            "given_quantity": trade.given_quantity,
        }),
    })

    msg = Message.objects.create(message=MODIFIED_MESSAGE, room=room, sender=message.user, msg_type=2)
    room.send_message(msg)


@channel_session_user
def trade_delete(message):
    trade = get_object_or_404(TradeRequest, pk=int(message['trade']))
    room = get_room_or_error(message["room"], message.user)
    pk = trade.pk
    trade.delete()
    room.websocket_group.send({
        "text": json.dumps({
            "delete": pk,
        }),
    })
    room.active = False

    msg = Message.objects.create(message=DECLINED_MESSAGE, room=room, sender=message.user, msg_type=2)
    room.send_message(msg)