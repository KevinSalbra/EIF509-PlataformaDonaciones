from django.urls import path

from .entrega_views import EntregaDetalleView, EntregaListaView
from .publicar_donacion_view import PublicarDonacionView
from .solicitud_views import AceptarSolicitudView, SolicitudDetalleView, SolicitudListaView
from .usuario_views import UsuarioDetalleView, UsuarioListaView
from .views import VistaSalud

urlpatterns = [
    path("salud", VistaSalud.as_view(), name="salud"),
    path("solicitudes", SolicitudListaView.as_view(), name="solicitudes"),
    path(
        "solicitudes/<int:id_solicitud>",
        SolicitudDetalleView.as_view(),
        name="solicitud_detalle",
    ),
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
    path("usuarios", UsuarioListaView.as_view(), name="usuarios"),
    path(
        "usuarios/<int:id_usuario>",
        UsuarioDetalleView.as_view(),
        name="usuario_detalle",
    ),
    path("entregas", EntregaListaView.as_view(), name="entregas"),
    path(
        "entregas/<int:id_entrega>",
        EntregaDetalleView.as_view(),
        name="entrega_detalle",
    ),
]