"""
URL configuration for config project.
"""

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from cr.ac.una.alimentaCR.presentation.views import VistaHealth


urlpatterns = [
    # A02: se retiro /admin/ (django.contrib.admin). El esquema lo gestiona
    # Flyway, no hay tablas de auth de Django y el panel propio (/panel/)
    # cubre la administracion; una ruta sin uso solo amplia la superficie.

    # Health check para la plataforma (Render). Sin detalles internos.
    path("actuator/health", VistaHealth.as_view(), name="actuator_health"),

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