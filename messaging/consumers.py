import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_type = self.scope['url_route']['kwargs']['room_type']
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'chat_{self.room_type}_{self.room_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.set_status('online')

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return
        msg_type = data.get('type','message')
        if msg_type == 'message':
            content = data.get('content','').strip()
            if not content:
                return
            msg = await self.save_message(content)
            if msg:
                await self.channel_layer.group_send(self.group_name, {'type':'chat_message','data':msg.to_dict()})
        elif msg_type == 'typing':
            await self.channel_layer.group_send(self.group_name, {'type':'typing_notify','user_id':self.user.id,'user_name':self.user.get_display_name(),'is_typing':data.get('is_typing',False)})
        elif msg_type == 'delete':
            msg_id = data.get('msg_id')
            deleted = await self.delete_message(msg_id)
            if deleted:
                await self.channel_layer.group_send(self.group_name, {'type':'message_deleted','msg_id':msg_id})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type':'message','data':event['data']}))

    async def typing_notify(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({'type':'typing','user_id':event['user_id'],'user_name':event['user_name'],'is_typing':event['is_typing']}))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({'type':'deleted','msg_id':event['msg_id']}))

    @database_sync_to_async
    def save_message(self, content):
        from .models import Message, DirectConversation
        from workspace.models import Channel
        try:
            if self.room_type == 'channel':
                channel = Channel.objects.get(id=self.room_id)
                if not channel.project.members.filter(id=self.user.id).exists():
                    return None
                return Message.objects.create(channel=channel, sender=self.user, content=content)
            elif self.room_type == 'dm':
                conv = DirectConversation.objects.get(id=self.room_id)
                if not conv.participants.filter(id=self.user.id).exists():
                    return None
                msg = Message.objects.create(conversation=conv, sender=self.user, content=content)
                conv.save()
                return msg
        except Exception:
            return None

    @database_sync_to_async
    def delete_message(self, msg_id):
        from .models import Message
        try:
            msg = Message.objects.get(id=msg_id, sender=self.user)
            msg.is_deleted = True
            msg.save(update_fields=['is_deleted'])
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def set_status(self, status):
        self.user.status = status
        self.user.save(update_fields=['status'])
