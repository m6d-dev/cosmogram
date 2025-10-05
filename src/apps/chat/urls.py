from django.urls import path
from . import views

urlpatterns = [
    path("", views.ChatAPIView.as_view({"post": "post", "update": "update",})),
    path("message/", views.MessageAPIView.as_view({"post":"post"})),
    # path("message/", view=views.MessageAPIView),
]

