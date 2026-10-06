from django.urls import path

from .entrega_views import EntregaDetalleView, EntregaListaView
from .donacion_views import DonacionDetalleView, DonacionListaView, PublicarDonacionView
from .solicitud_views import AceptarSolicitudView, SolicitudDetalleView, SolicitudListaView
from .usuario_views import UsuarioDetalleView, UsuarioListaView
from .views import VistaSalud
from .organizacion_views import OrganizacionDetalleView,OrganizacionListaView
from .categoria_views import CategoriaDetalleView,CategoriaListaView
from .auth_views import LoginView

urlpatterns = [
    path("salud", VistaSalud.as_view(), name="salud"),
    path("solicitudes", SolicitudListaView.as_view(), name="solicitudes"),
    path("solicitudes/<int:id_solicitud>",SolicitudDetalleView.as_view(),name="solicitud_detalle"),
    path("solicitudes/<int:id_solicitud>/aceptar",AceptarSolicitudView.as_view(),name="aceptar_solicitud"),

    path("donaciones",DonacionListaView.as_view(),name="donacion_lista"),
    path("donaciones/<int:id_donacion>",DonacionDetalleView.as_view(),name="donacion_detalle"),
    path("donaciones/publicar",PublicarDonacionView.as_view(),name="publicar_donacion"),

    path("usuarios", UsuarioListaView.as_view(), name="usuarios"),
    path("usuarios/<int:id_usuario>",UsuarioDetalleView.as_view(),name="usuario_detalle"),

    path("entregas", EntregaListaView.as_view(), name="entregas"),
    path("entregas/<int:id_entrega>", EntregaDetalleView.as_view(), name="entrega_detalle"),

    path("organizaciones", OrganizacionListaView.as_view(), name="organizacion_lista"),
    path("organizaciones/<int:id_organizacion>", OrganizacionDetalleView.as_view(),name="organizacion_detalle"),

    path("categorias",CategoriaListaView.as_view(),name="categoria_lista"),
    path("categorias/<int:id_categoria>",CategoriaDetalleView.as_view(),name="categoria_detalle"),

    path("auth/login", LoginView.as_view(), name="auth_login"),
]