from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.apps.content.views import CommentAPIView, LikeAPIView, PostAPIView

router = DefaultRouter()

router.register("post", PostAPIView, basename="posts")
router.register("like", LikeAPIView, basename="likes")
router.register("comment", CommentAPIView, basename="comments")

urlpatterns = [path("", include(router.urls))]
