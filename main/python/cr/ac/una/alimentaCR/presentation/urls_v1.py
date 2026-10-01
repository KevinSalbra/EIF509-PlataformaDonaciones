from django.urls import path

from .publicar_donacion_view import PublicarDonacionView
from .solicitud_views import AceptarSolicitudView
from .views import VistaSalud

urlpatterns = [
    path("salud", VistaSalud.as_view(), name="salud"),
    path(
        "solicitudes/<int:id_solicitud>/aceptar",
        AceptarSolicitudView.as_view(),
        name="aceptar_solicitud",
    ),
    path(
        "donaciones/publicar",
        PublicarDonacionView.as_view(),
        name="publicar_donacion",
    ),
]