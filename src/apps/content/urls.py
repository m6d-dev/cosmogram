from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.apps.content.views import PostAPIView

router = DefaultRouter()

router.register("post", PostAPIView, basename="posts")

urlpatterns = [path("", include(router.urls))]
