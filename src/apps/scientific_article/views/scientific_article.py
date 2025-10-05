from http import HTTPMethod

from django.db.models import Prefetch
from rest_framework.viewsets import ModelViewSet

from src.apps.scientific_article.models import ScientificArticleImage, ScientificArticle
from src.apps.scientific_article.serializers.scientific_article import ScientificArticleListSerializer, \
    ScientificArticleDetailSerializer, ScientificArticleCreateSerializer


class ScientificArticleViewSet(ModelViewSet):
    http_method_names = [ HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.DELETE ]

    def get_queryset(self):
        image_link_qs = ScientificArticleImage.objects.select_related("image").order_by("id")
        return (
            ScientificArticle.objects
            .select_related("file")
            .prefetch_related(
                "tags",
                Prefetch("scientificarticleimage_set", queryset=image_link_qs, to_attr="prefetched_images"),
            )
            .order_by("title")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ScientificArticleListSerializer
        if self.action == "retrieve":
            return ScientificArticleDetailSerializer
        if self.action == "create":
            return ScientificArticleCreateSerializer
        return ScientificArticleDetailSerializer
