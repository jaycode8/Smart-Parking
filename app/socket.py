import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class WebSocket(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.type = "notification"
        async_to_sync(self.channel_layer.group_add)(
            self.type, self.channel_name
        )
        # self.send(text_data=json.dumps({"message": message}))

    def disconnect(self, close_code):
        print(f"WebSocket disconnected with code {close_code}")

    def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received WebSocket message: {data}")
        self.send(text_data=json.dumps({"response": "Message received"}))

    def send_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))