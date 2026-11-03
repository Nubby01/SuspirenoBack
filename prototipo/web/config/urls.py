"""URLs del proyecto."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

admin.site.site_header = "Suspireño"
admin.site.site_title = "Suspireño"
admin.site.index_title = "Datos del negocio"

urlpatterns = [
    path("admin-django/", admin.site.urls),
    path("", include("pasteleria.urls")),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]

handler403 = "pasteleria.views.publico.permiso_denegado"
