# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

from .models import Message

def chat_group_name(user1_id: int, user2_id: int) -> str:
    a, b = sorted([int(user1_id), int(user2_id)])
    return f"chat_{a}_{b}"

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user = user
        self.groups = set()

        personal = f"user-{self.user.id}"
        print(self.channel_layer)
        await self.channel_layer.group_add(personal, self.channel_name)
        self.groups.add(personal)

        await self.accept()

    async def receive_json(self, content, **kwargs):
        """
        Ожидаемые команды от клиента:
        - {"command": "join", "other_id": 42}
        - {"command": "leave", "other_id": 42}
        - {"command": "message", "to": 42, "text": "hi"}
        - {"command": "history", "other_id": 42, "limit": 50}
        """
        cmd = content.get("command")
        if cmd == "join":
            other_id = content.get("other_id")
            if not other_id:
                await self.send_json({"error": "other_id required for join"})
                return
            group = chat_group_name(self.user.id, other_id)
            await self.add_group(group)
            msgs = await self.get_last_messages(self.user.id, other_id, limit=50)
            await self.send_json({"command": "history", "messages": msgs})
            return

        if cmd == "leave":
            other_id = content.get("other_id")
            if not other_id:
                return
            group = chat_group_name(self.user.id, other_id)
            await self.remove_group(group)
            return

        if cmd == "history":
            other_id = content.get("other_id")
            limit = int(content.get("limit", 50))
            msgs = await self.get_last_messages(self.user.id, other_id, limit=limit)
            await self.send_json({"command": "history", "messages": msgs})
            return

        if cmd == "message":
            to_id = content.get("to")
            text = content.get("text", "").strip()
            if not to_id or not text:
                await self.send_json({"error": "to and text required"})
                return

            recipient = await self.get_user_or_none(to_id)
            if not recipient:
                await self.send_json({"error": "recipient not found"})
                return
            message = await self.create_message(self.user.id, recipient.id, text)
            payload = {
                "id": message.id,
                "from": self.user.id,
                "to": recipient.id,
                "text": message.text,
                "created_at": message.created_at.isoformat(),
            }
            group = chat_group_name(self.user.id, recipient.id)
            await self.add_group(group)
            await self.channel_layer.group_send(
                group,
                {
                    "type": "chat.message",  
                    "message": payload,
                },
            )
            return

        await self.send_json({"error": "unknown command", "received": cmd})

    async def chat_message(self, event):
        """Тип события group_send -> отправляем на WS"""
        await self.send_json({"command": "message", "message": event["message"]})

    async def add_group(self, group_name: str):
        if group_name not in self.groups:
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.groups.add(group_name)

    async def remove_group(self, group_name: str):
        if group_name in self.groups:
            await self.channel_layer.group_discard(group_name, self.channel_name)
            self.groups.discard(group_name)

    async def disconnect(self, code):
        for group in list(self.groups):
            try:
                await self.channel_layer.group_discard(group, self.channel_name)
            except Exception:
                pass

    @database_sync_to_async
    def get_user_or_none(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, from_id, to_id, text):
        msg = Message.objects.create(
            sender_id=from_id,
            recipient_id=to_id,
            text=text,
            created_at=timezone.now(),
        )
        return msg

    @database_sync_to_async
    def get_last_messages(self, user1_id, user2_id, limit=50):
        a, b = sorted([int(user1_id), int(user2_id)])
        qs = Message.objects.filter(
        ).filter(
            (Q(sender_id=a) & Q(recipient_id=b)) | (Q(sender_id=b) & Q(recipient_id=a))
        ).order_by("-created_at")[:limit]
        return [
            {
                "id": m.id,
                "from": m.sender_id,
                "to": m.recipient_id,
                "text": m.text,
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(qs)
        ]
