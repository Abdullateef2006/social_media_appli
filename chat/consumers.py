import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from .models import Message
import base64

online_users = set()  # Keep track of online users

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        
        # Add user to the online list
        online_users.add(self.user.username)

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify the group that a user has come online and send the updated user list
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status_update',
                'online_users': list(online_users),
            }
        )

    async def disconnect(self, close_code):
        # Remove user from the online list
        online_users.discard(self.user.username)

        # Notify the group that a user has gone offline and send the updated user list
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status_update',
                'online_users': list(online_users),
            }
        )

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

        # Prepare to save a message
        new_message = Message(user=user, room_name=self.room_name, content=message)

        # Handle file uploads if present
        if file_data:
            file_name = file_data.get('name')
            file_content = base64.b64decode(file_data['content'])
            new_message.file.save(file_name, ContentFile(file_content), save=False)

        # Save the message to the database
        await sync_to_async(new_message.save)()

        # Send the message data to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': user.username,
                'message': message,
                'file_url': new_message.file.url if new_message.file else '',
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
            'file_url': event.get('file_url', ''),
            'timestamp': event['timestamp'],
        }))

    async def user_status_update(self, event):
        # Send the updated list of online users to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_status_update',
            'online_users': event['online_users'],
        })) 
        
        
# yourapp/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Notify group that a user has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_join',
                'message': f"{self.username} has joined the chat!"
            }
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Notify group that a user has left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_leave',
                'message': f"{self.username} has left the chat!"
            }
        )

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.username}: {message}"
            }
        )

    # Handle broadcasting join message
    async def chat_join(self, event):
        message = event['message']

        # Send the join message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'join'
        }))

    # Handle broadcasting leave message
    async def chat_leave(self, event):
        message = event['message']

        # Send the leave message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'leave'
        }))

    # Handle broadcasting chat messages
    async def chat_message(self, event):
        message = event['message']

        # Send the chat message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'message'
        }))
