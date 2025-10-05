from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path

application = get_asgi_application()  # noqa


from rest_framework_simplejwt.tokens import AccessToken  # noqa
from django.contrib.auth.models import AnonymousUser  # noqa
from rest_framework_simplejwt.exceptions import TokenError  # noqa

from src.apps.accounts.models import User  # noqa
from src.apps.chat.consumers import ChatConsumer  # noqa


django_asgi_app = get_asgi_application()


async def get_user(user_id):
    return await User.objects.aget(id=user_id)


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
