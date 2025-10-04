from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    groups: set
    
    async def connect(self):
        self.groups = set()
        self.user = self.scope["user"]
        group = f"user-{self.user.id}"
        await self.add_group(group)
        await self.accept()
        
    async def add_group(self, group):
        await self.channel_layer.group_add(group, self.channel_name)
        self.groups.add(group)
        
    async def recieve_json(self, content, **kwargs):
        pass
        
    async def disconnect(self, code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        await self.close()
    