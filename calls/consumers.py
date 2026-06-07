import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group = f'call_{self.room_id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.group, {'type':'peer_joined','user_id':self.user.id,'user_name':self.user.get_display_name(),'user_initials':self.user.get_initials(),'sender_channel':self.channel_name})

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.group, {'type':'peer_left','user_id':self.user.id,'user_name':self.user.get_display_name()})
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return
        t = data.get('type')
        target = data.get('target_id')
        if t == 'offer':
            await self.channel_layer.group_send(self.group, {'type':'webrtc_offer','sdp':data['sdp'],'from_id':self.user.id,'target_id':target})
        elif t == 'answer':
            await self.channel_layer.group_send(self.group, {'type':'webrtc_answer','sdp':data['sdp'],'from_id':self.user.id,'target_id':target})
        elif t == 'ice':
            await self.channel_layer.group_send(self.group, {'type':'webrtc_ice','candidate':data['candidate'],'from_id':self.user.id,'target_id':target})
        elif t == 'control':
            await self.channel_layer.group_send(self.group, {'type':'call_control','action':data.get('action'),'user_id':self.user.id,'value':data.get('value')})

    async def peer_joined(self, event):
        await self.send(text_data=json.dumps({'type':'peer_joined','user_id':event['user_id'],'user_name':event['user_name'],'user_initials':event['user_initials']}))

    async def peer_left(self, event):
        await self.send(text_data=json.dumps({'type':'peer_left','user_id':event['user_id']}))

    async def webrtc_offer(self, event):
        tid = event.get('target_id')
        if tid is None or tid == self.user.id:
            await self.send(text_data=json.dumps({'type':'offer','sdp':event['sdp'],'from_id':event['from_id']}))

    async def webrtc_answer(self, event):
        tid = event.get('target_id')
        if tid is None or tid == self.user.id:
            await self.send(text_data=json.dumps({'type':'answer','sdp':event['sdp'],'from_id':event['from_id']}))

    async def webrtc_ice(self, event):
        tid = event.get('target_id')
        if tid is None or tid == self.user.id:
            await self.send(text_data=json.dumps({'type':'ice','candidate':event['candidate'],'from_id':event['from_id']}))

    async def call_control(self, event):
        await self.send(text_data=json.dumps({'type':'control','action':event['action'],'user_id':event['user_id'],'value':event['value']}))
