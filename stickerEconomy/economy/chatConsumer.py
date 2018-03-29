from channels.generic.websocket import JsonWebsocketConsumer

class ChatConsumer(JsonWebsocketConsumer):

    def websocket_connect(self, event):
        self.accept()
        self.send_json({
            "accept": True,
        })

    def websocket_receive(self, event):
        payload = self.receive_json(event)
        # payload['reply_channel'] = message.content['reply_channel']
        # Channel("chat.receive").send(payload)
        self.send_json({
            "type": "websocket.send",
            "text": event,
        })

    # def websocket_disconnect(self, event):
        # for room_id in message.channel_session.get("rooms", set()):
        #     try:
        #         room = Room.objects.get(pk=room_id)
        #         # Removes us from the room's send group. If this doesn't get run,
        #         # we'll get removed once our first reply message expires.
        #         room.websocket_group.discard(message.reply_channel)
        #     except Room.DoesNotExist:
        #         pass