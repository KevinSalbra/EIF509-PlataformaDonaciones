"""
Pruebas de integracion de la API de Solicitud (/api/v1/solicitudes).

Usan la base PostgreSQL de Testcontainers con el esquema y los datos de
prueba de Flyway. Cada prueba corre dentro de una transaccion que se
revierte al terminar.

Datos de prueba usados:
- Usuario 2: representante donante, organizacion 2.
- Usuario 4: representante beneficiaria, organizacion 4.
- Usuario 5: representante beneficiaria, organizacion 5.
- Donaciones: 1 y 6 DISPONIBLES, 2 ASIGNADA.
- Solicitudes: 1 PENDIENTE (org 4, donacion 1),
  3 ACEPTADA y 6 CANCELADA.
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Solicitud, Usuario


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/solicitudes"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


@pytest.fixture
def usuario_donante():
    return Usuario.objects.get(pk=2)


@pytest.fixture
def usuario_beneficiario():
    return Usuario.objects.get(pk=4)


@pytest.fixture
def otro_usuario_beneficiario():
    return Usuario.objects.get(pk=5)


@pytest.fixture
def usuario_administrador():
    return Usuario.objects.get(pk=1)


def autenticar_cliente(cliente, usuario):
    token = AuthService.generar_token(usuario)

    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )


# ----------------------------------------------------------------
# GET
# ----------------------------------------------------------------

def test_listar_solicitudes_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json()["count"] >= 6


def test_obtener_solicitud_200(cliente):
    respuesta = cliente.get(f"{URL}/1")

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()

    assert cuerpo["id_solicitud"] == 1
    assert cuerpo["id_donacion"] == 1
    assert cuerpo["id_organizacion_beneficiaria"] == 4
    assert cuerpo["estado"] == "PENDIENTE"


def test_obtener_solicitud_inexistente_404(cliente):
    respuesta = cliente.get(f"{URL}/999999")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# POST
# ----------------------------------------------------------------

def test_crear_solicitud_201_con_location(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 6,
            "observacion": "Necesitamos esto",
        },
        format="json",
    )

    assert respuesta.status_code == 201

    cuerpo = respuesta.json()

    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["id_donacion"] == 6
    assert cuerpo["id_organizacion_beneficiaria"] == 4

    assert respuesta["Location"].endswith(
        f"{URL}/{cuerpo['id_solicitud']}"
    )


def test_crear_solicitud_y_consultarla_con_el_location(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    creada = cliente.post(
        URL,
        {
            "id_donacion": 6,
        },
        format="json",
    )

    assert creada.status_code == 201

    consulta = cliente.get(
        creada["Location"]
    )

    assert consulta.status_code == 200
    assert consulta.json()["id_donacion"] == 6


def test_crear_solicitud_cuerpo_vacio_400(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.post(
        URL,
        {},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA

    errores = respuesta.json()["errores"]

    assert "id_donacion" in errores


def test_crear_solicitud_observacion_vacia_400(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 6,
            "observacion": "   ",
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "observacion" in respuesta.json()["errores"]


def test_crear_solicitud_donacion_inexistente_404(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 999999,
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_donacion_no_disponible_409(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    # La donacion 2 esta ASIGNADA.
    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 2,
        },
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_duplicada_409(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    # La organizacion 4 ya tiene una solicitud pendiente
    # sobre la donacion 1.
    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 1,
        },
        format="json",
    )

    assert respuesta.status_code == 409


# ----------------------------------------------------------------
# SEGURIDAD POST
# ----------------------------------------------------------------

def test_crear_solicitud_sin_token_401(
    cliente,
):
    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 6,
        },
        format="json",
    )

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_crear_solicitud_donante_403(
    cliente,
    usuario_donante,
):
    autenticar_cliente(
        cliente,
        usuario_donante,
    )

    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 6,
        },
        format="json",
    )

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_administrador_403(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        {
            "id_donacion": 6,
        },
        format="json",
    )

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# DELETE
# ----------------------------------------------------------------

def test_cancelar_solicitud_204(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.delete(
        f"{URL}/1"
    )

    assert respuesta.status_code == 204

    assert (
        Solicitud.objects.get(pk=1).estado
        == "CANCELADA"
    )


def test_cancelar_solicitud_inexistente_404(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.delete(
        f"{URL}/999999"
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_cancelar_solicitud_de_otra_organizacion_403(
    cliente,
    otro_usuario_beneficiario,
):
    # La solicitud 1 pertenece a la organizacion 4.
    # El usuario 5 pertenece a la organizacion 5.
    autenticar_cliente(
        cliente,
        otro_usuario_beneficiario,
    )

    respuesta = cliente.delete(
        f"{URL}/1"
    )

    assert respuesta.status_code == 403

    assert (
        Solicitud.objects.get(pk=1).estado
        == "PENDIENTE"
    )


def test_cancelar_solicitud_aceptada_409(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.delete(
        f"{URL}/3"
    )

    assert respuesta.status_code == 409


def test_cancelar_solicitud_ya_cancelada_409(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.delete(
        f"{URL}/6"
    )

    assert respuesta.status_code == 409


# ----------------------------------------------------------------
# SEGURIDAD DELETE
# ----------------------------------------------------------------

def test_cancelar_solicitud_sin_token_401(
    cliente,
):
    respuesta = cliente.delete(
        f"{URL}/1"
    )

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_cancelar_solicitud_donante_403(
    cliente,
    usuario_donante,
):
    autenticar_cliente(
        cliente,
        usuario_donante,
    )

    respuesta = cliente.delete(
        f"{URL}/1"
    )

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# ACEPTAR
# ----------------------------------------------------------------

def test_aceptar_solicitud_inexistente_404(
    cliente,
    usuario_donante,
):
    autenticar_cliente(
        cliente,
        usuario_donante,
    )

    respuesta = cliente.post(
        f"{URL}/999999/aceptar",
        {},
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_aceptar_solicitud_no_pendiente_409(
    cliente,
    usuario_donante,
):
    autenticar_cliente(
        cliente,
        usuario_donante,
    )

    respuesta = cliente.post(
        f"{URL}/3/aceptar",
        {},
        format="json",
    )

    assert respuesta.status_code == 409


# ----------------------------------------------------------------
# SEGURIDAD ACEPTAR
# ----------------------------------------------------------------

def test_aceptar_solicitud_sin_token_401(
    cliente,
):
    respuesta = cliente.post(
        f"{URL}/1/aceptar",
        {},
        format="json",
    )

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_aceptar_solicitud_beneficiario_403(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(
        cliente,
        usuario_beneficiario,
    )

    respuesta = cliente.post(
        f"{URL}/1/aceptar",
        {},
        format="json",
    )

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_aceptar_solicitud_administrador_403(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        f"{URL}/1/aceptar",
        {},
        format="json",
    )

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA