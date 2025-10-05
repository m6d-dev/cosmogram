from rest_framework.viewsets import ModelViewSet, GenericViewSet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from src.apps.content.models.comment import Comment
from src.apps.content.models.like import Like
from src.apps.content.models.post import Post
from src.apps.content.serializers import (
    CommentSerializer,
    LikeSerializer,
    ListPostSerializer,
    PostSerializer,
)
from src.apps.content.services.post import post_service
from src.apps.content.services.comment import comment_service
from src.apps.content.services.like import like_service
from src.utils.conts import ViewAction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.utils.functions import raise_validation_error_detail
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(tags=["content"])
class PostAPIView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ("created_by",)
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
        return post_service.all().order_by("-created_by")

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
    

    serializer_class = LikeSerializer

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


@extend_schema(tags=["content"])
class CommentAPIView(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"
    model = Comment

    def get_queryset(self):
        return comment_service.filter(created_by_id=self.request.user.id)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "add_comment":
            return CommentSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"], url_path="add")
    def add_comment(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request, "user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
