from functools import wraps

from .exceptions import ClientError
from .models import Room


def catch_client_error(func):
    """
    Decorator to catch the ClientError exception and translate it into a reply.
    """
    @wraps(func)
    def inner(message, *args, **kwargs):
        try:
            return func(message, *args, **kwargs)
        except ClientError as e:
            print(e)
            # If we catch a client error, tell it to send an error string
            # back to the client on their reply channel
            e.send_to(message.reply_channel)
    return inner


def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    # Check permissions
    return room

def give_stickers(sticker, quantity):
    if sticker.quantity == quantity:
        sticker.delete()
    else:
        sticker.quantity -= quantity
        sticker.save()


def trade_stickers(trade):
    give_stickers(trade.given_sticker, trade.given_quantity)
    give_stickers(trade.requested_sticker, trade.requested_quantity)
    trade.delete()