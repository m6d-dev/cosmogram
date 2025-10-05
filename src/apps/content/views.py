from rest_framework.viewsets import ModelViewSet, GenericViewSet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from src.apps.content.models.like import Like
from src.apps.content.models.post import Post
from src.apps.content.serializers import ListPostSerializer, PostSerializer
from src.apps.content.services.post import post_service
from src.apps.content.services.like import like_service
from src.utils.conts import ViewAction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.utils.functions import raise_validation_error_detail
from rest_framework.decorators import action


@extend_schema(tags=["content"])
class PostAPIView(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    model = Post

    def get_serializer_class(self):
        if self.action in [
            ViewAction.CREATE,
            ViewAction.UPDATE,
            ViewAction.PARTIAL_UPDATE,
        ]:
            return PostSerializer
        return ListPostSerializer

    def get_queryset(self):
        return post_service.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.model.objects.filter(
            id=kwargs.get("id"), created_by_id=request.user.id
        )
        if not instance:
            raise_validation_error_detail({"data": "Not found"})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["content"])
class LikeAPIView(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"
    model = Like

    def get_queryset(self):
        return like_service.filter(created_by_id=self.request.user.id)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="post_id",
                type=OpenApiTypes.INT,
                required=True,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    @action(detail=False, methods=["post"], url_path="add")
    def add_like(self, request, *args, **kwargs):
        """
        Custom action to add a like by post_id instead of like_id.
        """
        post_id = request.query_params.get("post_id")
        if not post_id:
            raise_validation_error_detail("post_id is required")

        like = like_service.exists(post_id=post_id, created_by_id=request.user.id)
        if like:
            raise_validation_error_detail("You have liked this post")

        like_service.create(post_id=post_id, created_by_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="post_id",
                type=OpenApiTypes.INT,
                required=True,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    @action(detail=False, methods=["delete"], url_path="remove")
    def remove_like(self, request, *args, **kwargs):
        """
        Custom action to delete a like by post_id instead of like_id.
        """
        post_id = request.query_params.get("post_id")
        if not post_id:
            raise_validation_error_detail("post_id is required")

        like = like_service.filter(
            post_id=post_id, created_by_id=request.user.id
        ).first()
        if not like:
            raise_validation_error_detail("You haven't liked this post")

        like_service.delete(instance=like, post_id=post_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
