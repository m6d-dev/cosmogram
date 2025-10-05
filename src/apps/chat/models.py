from django.db import models

from src.apps.accounts.models import User
from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Chat(AbstractTimestampsModel):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_user2")

    class Meta:
        unique_together = (("user1", "user2"),)
        indexes = [
            models.Index(fields=["user1", "user2"]),
            models.Index(fields=["updated_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.user1_id == self.user2_id:
            raise ValueError("Chat должен быть между двумя разными пользователями")
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def other_user(self, user):
        return self.user2 if user.id == self.user1_id else self.user1

    def __str__(self):
        return f"Chat({self.user1_id},{self.user2_id})"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()  # TextField — нормально для длинных сообщений
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    def __str__(self):
        return f"Message({self.id}) in Chat({self.chat_id}) from {self.sender_id}"

