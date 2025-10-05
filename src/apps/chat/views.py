from rest_framework.viewsets import ModelViewSet
from src.apps.chat.models import Chat, Message


class ChatAPIView(ModelViewSet):
    def post(self, request):
        return Chat.objects.create()


class MessageAPIView(ModelViewSet):
    def post(self, request):
        return Message.objects.create()
