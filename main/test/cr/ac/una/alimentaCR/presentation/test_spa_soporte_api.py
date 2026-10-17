"""
Pruebas del soporte de la API para la SPA (Laboratorio 6):
- GET /api/v1/categorias/activas (lectura para cualquier rol).
- CORS: solo el origen configurado de la SPA puede llamar a la API.

Datos de prueba: Usuario 1 = ADMINISTRADOR, Usuario 2 =
REPRESENTANTE_DONANTE, Categoria 6 = Bebidas, INACTIVA.
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Categoria, Usuario

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/categorias/activas"
ORIGEN_SPA = "http://localhost:5173"


@pytest.fixture
def cliente():
    return APIClient()


def autenticar(cliente, id_usuario):
    token = AuthService.generar_token(Usuario.objects.get(pk=id_usuario))
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


def test_categorias_activas_sin_token_401(cliente):
    assert cliente.get(URL).status_code == 401


@pytest.mark.parametrize("id_usuario", [1, 2])
def test_categorias_activas_permite_administrador_y_donante(
    cliente, id_usuario
):
    autenticar(cliente, id_usuario)

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == Categoria.objects.filter(
        estado=Categoria.Estado.ACTIVA
    ).count()
    assert set(datos[0]) == {"id_categoria", "nombre"}


def test_categorias_activas_excluye_inactivas(cliente):
    autenticar(cliente, 2)
    ids = {c["id_categoria"] for c in cliente.get(URL).json()}
    inactivas = set(
        Categoria.objects.filter(
            estado=Categoria.Estado.INACTIVA
        ).values_list("id_categoria", flat=True)
    )
    assert inactivas and not (ids & inactivas)


def test_listado_completo_de_categorias_sigue_siendo_del_administrador(
    cliente,
):
    autenticar(cliente, 2)
    assert cliente.get("/api/v1/categorias").status_code == 403


def _preflight(cliente, origen):
    return cliente.options(
        "/api/v1/auth/login",
        HTTP_ORIGIN=origen,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
    )


def test_cors_permite_el_origen_de_la_spa(cliente, settings):
    # Se fija el origen para que la prueba no dependa del .env de nadie.
    settings.CORS_ALLOWED_ORIGINS = [ORIGEN_SPA]

    respuesta = _preflight(cliente, ORIGEN_SPA)

    assert respuesta["Access-Control-Allow-Origin"] == ORIGEN_SPA
    assert "authorization" in respuesta["Access-Control-Allow-Headers"]


def test_cors_rechaza_otros_origenes(cliente, settings):
    settings.CORS_ALLOWED_ORIGINS = [ORIGEN_SPA]

    respuesta = _preflight(cliente, "https://sitio-malicioso.example")

    assert "Access-Control-Allow-Origin" not in respuesta