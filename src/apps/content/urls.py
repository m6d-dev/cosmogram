from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.apps.content.views import LikeAPIView, PostAPIView

router = DefaultRouter()

router.register("post", PostAPIView, basename="posts")
router.register("like", LikeAPIView, basename="likes")

urlpatterns = [path("", include(router.urls))]
