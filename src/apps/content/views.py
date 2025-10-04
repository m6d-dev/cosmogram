from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from src.apps.content.serializers import PostSerializer
from src.apps.content.services.post import post_service


@extend_schema(tags=["content"])
class PostAPIView(ModelViewSet):
    queryset = post_service.all()

    def get_serializer_class(self):
        return PostSerializer
