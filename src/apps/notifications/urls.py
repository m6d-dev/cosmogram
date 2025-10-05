from django.urls import path, include
from rest_framework.decorators import api_view
from src.apps.accounts.models import User
from src.apps.notifications.services import PostLikeNotify
from src.apps.notifications.views import NotificationAPIView
from rest_framework_simplejwt.tokens import RefreshToken


@api_view()
def niga(request):
    user = User.objects.first()
    print(str(RefreshToken.for_user(user).access_token))
    a = PostLikeNotify(user, "NigerOne")
    a.notify()


urlpatterns = [path("", NotificationAPIView.as_view()), path("niga", niga)]
