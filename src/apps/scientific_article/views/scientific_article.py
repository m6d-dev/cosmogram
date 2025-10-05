from http import HTTPMethod

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet

from src.apps.scientific_article.models import ScientificArticleImage, ScientificArticle
from src.apps.scientific_article.serializers.scientific_article import (
    ScientificArticleListSerializer,
    ScientificArticleDetailSerializer,
    ScientificArticleCreateSerializer,
)


@extend_schema(tags=["scientific_article"])
class ScientificArticleViewSet(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
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
        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return ScientificArticleListSerializer
        if self.action == "retrieve":
            return ScientificArticleDetailSerializer
        if self.action == "create":
            return ScientificArticleCreateSerializer
        return ScientificArticleDetailSerializer
