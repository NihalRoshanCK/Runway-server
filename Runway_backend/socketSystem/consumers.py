from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import json
import asyncio


        

@database_sync_to_async
def get_notification_count(user):
    from socketSystem.models import Notification,NotificationContent
    return Notification.objects.filter(user=user, is_seen=False).count()

@database_sync_to_async
def get_all_new_notifications(user):
    from socketSystem.models import Notification,NotificationContent
    notifications = Notification.objects.filter(user=user)
    new_notifications = []
    for notification in notifications:
        message = notification.content.message
        created = notification.content.created_at.isoformat()
        id=notification.content.id
        new_notifications.append({
            'id': id,
            'message': message,
            'created': created
        })
    return new_notifications

@database_sync_to_async
def mark_notifications_as_seen(user):
    from socketSystem.models import Notification,NotificationContent
    notifications = Notification.objects.filter(user=user, is_seen=False)
    for notification in notifications:
        notification.is_seen = True
        notification.save()
        
@database_sync_to_async
def get_pending_notifications(user):
    from socketSystem.models import Notification,NotificationContent
    return list(Notification.objects.filter(user=user, is_seen=False))

@database_sync_to_async
def get_new_notifications(user):
    from socketSystem.models import Notification,NotificationContent
    notifications = Notification.objects.filter(user=user, is_seen=False).order_by('-created_at')[:3]
    new_notifications = []
    for notification in notifications:
        message = notification.content.message
        created = notification.content.created_at.isoformat()
        id=notification.content.id
        new_notifications.append({
            'id': id,
            'message': message,
            'created': created
        })
    return new_notifications

    
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close(code=1009)
            return
        await self.accept()
        
    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        user = self.scope['user']

        if action == 'mark_as_seen':
            await mark_notifications_as_seen(user)
        if action =='see_notification_count':
            await self.send_notification_count()
        if action =='see_notification':
            await self.send_notifications()
        if action =='see_all_notifications':
            await self.send_all_notifications()
    
    
        
    async def send_notification_count(self):
        user = self.scope['user']
        count = await get_notification_count(user)
        await self.send_json({'action': 'notification_count','notification_count': count})
    
    async def send_all_notifications(self):
        user = self.scope['user']
        notifications = await get_all_new_notifications(user)
        await self.send_json({'action': 'all_notification','notifications': notifications})
        
    async def send_notifications(self):
        user = self.scope['user']
        new_notifications = await get_new_notifications(user)
        if new_notifications:
            # for notification in new_notifications:
            await self.send_json({
                'action': 'new_notification',
                'notifications': new_notifications
            }) 

@database_sync_to_async
def get_hub(hub):
    from hubs.models import Hub
    try:
        hub=Hub.objects.get(id=hub)
    except Hub.DoesNotExist:
        hub=None
    return hub
@database_sync_to_async
def get_staff_hub(user):
    from auths.models import Staff
    try:
        staff=Staff.objects.get(user_id=user)
    except staff.DoesNotExist:
        staff=None
    return staff.hub
@database_sync_to_async

def get_staff(user):
    from auths.models import Staff
    from hubs.serializer import StaffSerializer 
    try:
        staff=Staff.objects.get(user_id=user)
    except staff.DoesNotExist:
        staff=None
    serializer = StaffSerializer(data=staff)
    serializer.is_valid(raise_exception=True)
    return serializer.data
@database_sync_to_async
def save_message(message:dict):
    from socketSystem.models import Message
    from socketSystem.serializers import MessageChannelSerializer
    serializer = MessageChannelSerializer(data=message)
    serializer.is_valid(raise_exception=True)
    serializer.save()
   
    return serializer.data
@database_sync_to_async
def serializeUser(user):
    from auths.models import CustomUser
    from auths.serializer import UserSerializer
    try:
        user=CustomUser.objects.get(id=user)
    except CustomUser.DoesNotExist:
        user=None
    sender_serializer = UserSerializer(user)
    return sender_serializer.data
class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.user = None
        self.hub=None

    async def connect(self):
        if not self.scope['user'].is_anonymous:
            self.user=self.scope['user']
            staff=get_staff(self.user.id)
            self.hub= await get_staff_hub(self.user.id)
            self.room_group_name = self.make_group_name()
            await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
            )
            await self.accept()
        else:
            await self.close(code=1009)
            return
            
    async def receive_json(self, content):
        message_type = content.get('type')
        if message_type == 'text':
            # Handle text message
            await self.handle_text_message(content)
        elif message_type == 'audio':
            # Handle audio file
            await self.handle_file_message(content, 'audio')
        elif message_type == 'video':
            # Handle video file
            await self.handle_file_message(content, 'video')

    async def handle_text_message(self, content):
        import datetime
        message_data = {
            "hub":self.hub.id,
            'sender': self.scope['user'].id,
            'content': content['content'],
            "message_type":"text",
            'timestamp': str(datetime.datetime.now()),
        }
        message=await save_message(message_data)
        sender_user = await serializeUser(self.scope['user'].id)
        # await self.send_group_message(message_data)
        message.pop("sender")
        message["sender"]=sender_user
        await self.send_group_message(message)

    async def handle_file_message(self, content, file_type):
        file_data = content.get('file_data')
        file_name = content.get('file_name')
        # Save the file to a temporary location (e.g., MEDIA_ROOT) or a storage backend
        # Ensure you validate and secure the uploaded file

        # Broadcast the file to other users in the same hub
        await self.send_group_file(file_data, file_name, file_type)

    async def send_group_file(self, file_data, file_name, file_type):
        # Broadcast the file to all users in the hub
        await self.channel_layer.group_add(self.hub_group_name(), self.channel_name)
        await self.channel_layer.group_send(
            self.hub_group_name(),
            {
                'type': 'group.file',
                'file_data': file_data,
                'file_name': file_name,
                'file_type': file_type,
            },
        )
    async def send_group_message(self, message_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                
                'type': 'text_message',
                "message_data":message_data,
            }
        )

    async def group_file(self, event):
        # Handle the broadcasted file message and send it to the client
        await self.send_json({
            'type': 'file',
            'file_data': event['file_data'],
            'file_name': event['file_name'],
            'file_type': event['file_type'],
        })
        
    async def text_message(self, event):
    # Send the text message to the WebSocket clients in the group
        await self.send_json({
            'type': 'text',
            "message":event,
        })

    def make_group_name(self):
        # hub_id = self.scope['url_route']['kwargs']['hub_id']
        return f'hub_{self.hub.id}'


































































