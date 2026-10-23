"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),
    path(
        "panel/",
        include(
            "cr.ac.una.alimentaCR.presentation.web.urls"
        ),
    ),
    path(
        "api/v1/",
        include(
            "cr.ac.una.alimentaCR.presentation.urls_v1"
        ),
    ),
]

# Errores 404 y 500 fuera de DRF (Problem Details para rutas /api/).
handler404 = "cr.ac.una.alimentaCR.presentation.exception_handler.manejador_404"
handler500 = "cr.ac.una.alimentaCR.presentation.exception_handler.manejador_500"