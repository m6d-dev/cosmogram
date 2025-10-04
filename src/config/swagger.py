from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.urls import path

urlpatterns = [
    path(
        route="api/v1/docs/schema/download/",
        view=SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        route="docs/",
        view=SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        route="redoc/",
        view=SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
