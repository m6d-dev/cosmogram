from django.urls import path, include

from src.apps.content.urls import DefaultRouter
from src.apps.scientific_article.views.scientific_article import (
    ScientificArticleViewSet,
)

router = DefaultRouter()

router.register(
    "",
    ScientificArticleViewSet,
    basename="scientific_article",
)

urlpatterns = [
    path("", include(router.urls)),
]
