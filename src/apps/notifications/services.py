from typing import Iterable
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from src.apps.accounts.models import User
from src.apps.notifications.models import Notification
from src.apps.notifications.serializers import NotificationSerializer
from src.utils.bases.services import AbstractEditService
from src.utils.conts import NotifcationType


class PostLikeNotify:
    def __init__(self, post_owner, liked_user_name):
        self.post_owner = post_owner
        self.liked_username = liked_user_name

    def notify(self):
        msg = f"{self.liked_username} liked your post"
        notification = create_notification(
            user_id=self.post_owner.id, content=msg, type=NotifcationType.POST_LIKED
        )
        send_notification(username=self.post_owner.username, notification=notification)


def create_notification(user_id, **kwargs):
    return Notification.objects.create(user_id=user_id, **kwargs)


def get_serializer_for_notification(notification):
    serializer = NotificationSerializer(notification)
    return serializer.data


def send_notification(username, notification):
    channel_layer = get_channel_layer()
    serializered_data = get_serializer_for_notification(notification=notification)
    async_to_sync(channel_layer.group_send)(
        username, {"type": "send_notification", "data": serializered_data}
    )
