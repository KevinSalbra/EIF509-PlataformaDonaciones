from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="panel_inicio"),
    path("login/", views.login, name="panel_login"),
    path("logout/", views.logout, name="panel_logout"),

    path("categorias/", views.categoria_lista, name="panel_categorias"),
    path("categorias/nueva/", views.categoria_crear, name="panel_categoria_crear"),
    path("categorias/<int:id_categoria>/editar/", views.categoria_editar, name="panel_categoria_editar"),

    path("organizaciones/", views.organizacion_lista, name="panel_organizaciones"),
    path("organizaciones/nueva/", views.organizacion_crear, name="panel_organizacion_crear"),
    path("organizaciones/<int:id_organizacion>/editar/", views.organizacion_editar, name="panel_organizacion_editar"),
]