from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from . import swagger


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("src.apps.accounts.urls")),
    path("api/content/", include("src.apps.content.urls")),
    path("api/scientific-articles/", include("src.apps.scientific_article.urls")),
    path("api/chat/", include("src.apps.chat.urls")),
    path("api/notifications/", include("src.apps.notifications.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += swagger.urlpatterns
