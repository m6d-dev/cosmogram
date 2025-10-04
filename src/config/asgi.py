from django.core.asgi import get_asgi_application
from cosmogram.src.apps.accounts.models import User

from rest_framework_simplejwt.tokens import AccessToken, Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.exceptions import TokenError

from cosmogram.src.apps.chat.consumers import ChatConsumer



application = get_asgi_application()



from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path


django_asgi_app = get_asgi_application()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()
    
    
class WebSocketJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()
        token = self.get_token_from_path(scope["path"])

        try:
            access_token = AccessToken(token)
            scope["user"] = await get_user(access_token["user_id"])
        except TokenError as e:
            raise TokenError("Invalid token") from e

        return await self.app(scope, receive, send)

    def get_token_from_path(self, path: str) -> str:
        return path.split("/")[-1]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(
            URLRouter(
                [
                    path(
                        r"ws/chat/<str:token>",
                        ChatConsumer.as_asgi(),
                    ),
                ]
            ),
        ),
    }
)





