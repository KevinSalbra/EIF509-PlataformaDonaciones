"""
Los procesos del dominio se exponen como recursos REST, sin verbos en
la ruta:

- Publicar una donacion  -> POST /api/v1/donaciones
- Aceptar una solicitud  -> POST /api/v1/solicitudes/<id>/entrega
  (aceptar crea la entrega de la solicitud)

Las rutas anteriores (/donaciones/publicar y /solicitudes/<id>/aceptar)
ya no existen y responden 404 con Problem Details.
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Usuario

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


def autenticar(cliente, id_usuario):
    token = AuthService.generar_token(Usuario.objects.get(pk=id_usuario))
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


@pytest.mark.parametrize(
    "ruta",
    [
        "/api/v1/donaciones/publicar",
        "/api/v1/solicitudes/1/aceptar",
    ],
)
def test_las_rutas_con_verbo_ya_no_existen(cliente, ruta):
    autenticar(cliente, 2)

    respuesta = cliente.post(ruta, {}, format="json")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)


def test_listar_donaciones_sigue_siendo_publico(cliente):
    assert cliente.get("/api/v1/donaciones").status_code == 200


def test_publicar_donacion_sin_token_401(cliente):
    respuesta = cliente.post("/api/v1/donaciones", {}, format="json")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


@pytest.mark.parametrize("id_usuario", [1, 4])  # administrador y beneficiaria
def test_publicar_donacion_solo_para_donantes_403(cliente, id_usuario):
    autenticar(cliente, id_usuario)

    respuesta = cliente.post("/api/v1/donaciones", {}, format="json")

    assert respuesta.status_code == 403


def test_aceptar_solicitud_sin_token_401(cliente):
    respuesta = cliente.post("/api/v1/solicitudes/1/entrega", {}, format="json")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


@pytest.mark.parametrize("id_usuario", [1, 4])  # administrador y beneficiaria
def test_aceptar_solicitud_solo_para_donantes_403(cliente, id_usuario):
    autenticar(cliente, id_usuario)

    respuesta = cliente.post("/api/v1/solicitudes/1/entrega", {}, format="json")

    assert respuesta.status_code == 403