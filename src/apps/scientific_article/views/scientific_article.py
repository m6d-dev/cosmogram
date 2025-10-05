from http import HTTPMethod

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from src.apps.scientific_article.models import (
    ScientificArticleImage,
    ScientificArticle,
    ScientificArticleLike,
    ScientificArticleComments,
)
from src.apps.scientific_article.serializers.scientific_article import (
    ScientificArticleListSerializer,
    ScientificArticleDetailSerializer,
    ScientificArticleCreateSerializer,
    ScientificArticleLikeCreateSerializer,
    ScientificArticleCommentListSerializer,
    ScientificArticleCommentCreateSerializer,
)
from src.utils.functions import normalize_strict


@extend_schema(tags=["scientific_article"])
class ScientificArticleViewSet(ModelViewSet):
    http_method_names = [
        HTTPMethod.GET.lower(),
        HTTPMethod.POST.lower(),
        HTTPMethod.DELETE.lower(),
    ]

    def get_queryset(self):
        image_link_qs = ScientificArticleImage.objects.select_related("image").order_by(
            "id"
        )
        return (
            ScientificArticle.objects.select_related("file")
            .prefetch_related(
                "tags",
                Prefetch(
                    "scientificarticleimage_set",
                    queryset=image_link_qs,
                    to_attr="prefetched_images",
                ),
            )
            .order_by("title")
        )

    def create(self, request, *args, **kwargs):
        print("DATA:", request.data)
        print("FILES:", request.FILES)
        payload = normalize_strict(request)
        print("PAYLOAD:", payload)
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action == "list":
            return ScientificArticleListSerializer
        if self.action == "retrieve":
            return ScientificArticleDetailSerializer
        if self.action == "create":
            return ScientificArticleCreateSerializer
        return ScientificArticleDetailSerializer


class ScientificArticleLikeAPIView(CreateAPIView):
    serializer_class = ScientificArticleLikeCreateSerializer
    lookup_url_kwarg = "article_id"

    http_method_names = [
        HTTPMethod.POST.lower(),
        HTTPMethod.DELETE.lower(),
    ]

    def get_queryset(self):
        return ScientificArticleLike.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.scientific_article.likes_count -= 1
        instance.scientific_article.save(update_fields=["likes_count"])
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScientificArticleCommentViewSet(DestroyAPIView, CreateAPIView):

    def get_queryset(self):
        return ScientificArticleComments.objects.all()

    def get_serializer_class(self):
        if self.request.method == HTTPMethod.GET.lower():
            return ScientificArticleCommentListSerializer
        return ScientificArticleCommentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.scientific_article.comments_count -= 1
        instance.scientific_article.save(update_fields=["comments_count"])
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
