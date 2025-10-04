from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from . import swagger


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("src.apps.accounts.urls")),
    path("api/content/", include("src.apps.content.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += swagger.urlpatterns
