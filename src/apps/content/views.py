from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from src.apps.content.models.post import Post
from src.apps.content.serializers import ListPostSerializer, PostSerializer
from src.apps.content.services.post import post_service
from src.utils.conts import ViewAction


@extend_schema(tags=["content"])
class PostAPIView(ModelViewSet):
    model = Post

    def get_serializer_class(self):
        if self.action in [
            ViewAction.CREATE,
            ViewAction.UPDATE,
            ViewAction.PARTIAL_UPDATE,
        ]:
            return PostSerializer
        return ListPostSerializer

    def create(self, request, *args, **kwargs):
        print(f"Here is data: {request.data}.")
        super().create(request, *args, **kwargs)

    def get_queryset(self):
        return post_service.filter(created_by_id=self.request.user.id)
