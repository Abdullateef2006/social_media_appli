# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.roomGroupName = "group_chat"
#         await self.channel_layer.group_add(
#             self.roomGroupName,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.roomGroupName,
#             self.channel_layer
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         username = text_data_json["username"]
#         time = text_data_json["time"]
#         await self.channel_layer.group_send(
#             self.roomGroupName, {
#                 "type": "sendMessage",
#                 "message": message,
#                 "username": username,
#                 "time": time
#             })

#     async def sendMessage(self, event):
#         message = event["message"]
#         username = event["username"]
#         time = event["time"]
#         await self.send(text_data=json.dumps({"message": message, "username": username, "time": time}))



# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Message
from asgiref.sync import sync_to_async
import base64

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        file_data = text_data_json.get('file', None)

        user = self.scope['user']

        # Create a new message instance
        new_message = Message(user=user, room_name=self.room_name, content=message)

        # Handle file uploads (if a file is included)
        if file_data:
            file_name = file_data.get('name')
            file_content = ContentFile(base64.b64decode(file_data['content']), name=file_name)
            new_message.file.save(file_name, file_content)

        # Save the message to the database
        await sync_to_async(new_message.save)()

        # Prepare message data to send to the group
        message_data = {
            'type': 'chat_message',
            'username': user.username,
            'message': message,
            'file_url': new_message.file.url if new_message.file else '',
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
            'file_url': event.get('file_url', ''),
            'timestamp': event['timestamp'],
        }))
