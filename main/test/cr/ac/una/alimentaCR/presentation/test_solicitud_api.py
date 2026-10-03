"""
Pruebas de integracion de la API de Solicitud (/api/v1/solicitudes).

Usan la base PostgreSQL de Testcontainers con el esquema y los datos de
prueba de Flyway. Cada prueba corre dentro de una transaccion que se
revierte al terminar.

Datos de prueba usados:
- Usuarios: 2 (donante, org 2), 4 y 5 (beneficiarios, orgs 4 y 5),
  6 (inactivo, org 6, beneficiaria PENDIENTE de aprobacion).
- Donaciones: 1 y 6 DISPONIBLES, 2 ASIGNADA.
- Solicitudes: 1 PENDIENTE (org 4, donacion 1), 3 ACEPTADA, 6 CANCELADA.
"""
import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.data.models import Solicitud

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/solicitudes"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


# ---------------------------------------------------------------- GET

def test_listar_solicitudes_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.json()) >= 6


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


# --------------------------------------------------------------- POST

def test_crear_solicitud_201_con_location(cliente):
    respuesta = cliente.post(
        URL,
        {"id_donacion": 6, "id_usuario": 4, "observacion": "Necesitamos esto"},
        format="json",
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["id_donacion"] == 6
    assert cuerpo["id_organizacion_beneficiaria"] == 4
    assert respuesta["Location"].endswith(f"{URL}/{cuerpo['id_solicitud']}")


def test_crear_solicitud_y_consultarla_con_el_location(cliente):
    creada = cliente.post(
        URL, {"id_donacion": 6, "id_usuario": 4}, format="json"
    )

    consulta = cliente.get(creada["Location"])

    assert consulta.status_code == 200
    assert consulta.json()["id_donacion"] == 6


def test_crear_solicitud_cuerpo_vacio_400(cliente):
    respuesta = cliente.post(URL, {}, format="json")

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    errores = respuesta.json()["errores"]
    assert "id_donacion" in errores
    assert "id_usuario" in errores


def test_crear_solicitud_observacion_vacia_400(cliente):
    respuesta = cliente.post(
        URL,
        {"id_donacion": 6, "id_usuario": 4, "observacion": "   "},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "observacion" in respuesta.json()["errores"]


def test_crear_solicitud_donacion_inexistente_404(cliente):
    respuesta = cliente.post(
        URL, {"id_donacion": 999999, "id_usuario": 4}, format="json"
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_usuario_inexistente_404(cliente):
    respuesta = cliente.post(
        URL, {"id_donacion": 6, "id_usuario": 999999}, format="json"
    )

    assert respuesta.status_code == 404


def test_crear_solicitud_donacion_no_disponible_409(cliente):
    # La donacion 2 esta ASIGNADA.
    respuesta = cliente.post(
        URL, {"id_donacion": 2, "id_usuario": 4}, format="json"
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_duplicada_409(cliente):
    # La organizacion 4 ya tiene la solicitud 1 pendiente sobre la donacion 1.
    respuesta = cliente.post(
        URL, {"id_donacion": 1, "id_usuario": 4}, format="json"
    )

    assert respuesta.status_code == 409


def test_crear_solicitud_organizacion_donante_422(cliente):
    # El usuario 2 pertenece a una organizacion DONANTE.
    respuesta = cliente.post(
        URL, {"id_donacion": 6, "id_usuario": 2}, format="json"
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_solicitud_organizacion_no_aprobada_422(cliente):
    # La organizacion 6 es beneficiaria pero esta PENDIENTE de aprobacion.
    nuevo_usuario = cliente.post(
        "/api/v1/usuarios",
        {
            "id_organizacion": 6,
            "nombre": "Pedro Rojas",
            "correo": "pedro.rojas@prueba.com",
            "contrasena": "ClaveSegura123",
            "rol": "REPRESENTANTE_BENEFICIARIA",
        },
        format="json",
    )
    assert nuevo_usuario.status_code == 201

    respuesta = cliente.post(
        URL,
        {"id_donacion": 6, "id_usuario": nuevo_usuario.json()["id_usuario"]},
        format="json",
    )

    assert respuesta.status_code == 422


# ------------------------------------------------------------- DELETE

def test_cancelar_solicitud_204(cliente):
    respuesta = cliente.delete(f"{URL}/1?id_usuario=4")

    assert respuesta.status_code == 204
    assert Solicitud.objects.get(pk=1).estado == "CANCELADA"


def test_cancelar_solicitud_sin_usuario_400(cliente):
    respuesta = cliente.delete(f"{URL}/1")

    assert respuesta.status_code == 400
    assert "id_usuario" in respuesta.json()["errores"]


def test_cancelar_solicitud_inexistente_404(cliente):
    respuesta = cliente.delete(f"{URL}/999999?id_usuario=4")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_cancelar_solicitud_de_otra_organizacion_403(cliente):
    # La solicitud 1 es de la organizacion 4; el usuario 5 es de la 5.
    respuesta = cliente.delete(f"{URL}/1?id_usuario=5")

    assert respuesta.status_code == 403
    assert Solicitud.objects.get(pk=1).estado == "PENDIENTE"


def test_cancelar_solicitud_aceptada_409(cliente):
    respuesta = cliente.delete(f"{URL}/3?id_usuario=4")

    assert respuesta.status_code == 409


def test_cancelar_solicitud_ya_cancelada_409(cliente):
    respuesta = cliente.delete(f"{URL}/6?id_usuario=4")

    assert respuesta.status_code == 409


# ------------------------------------------- ACEPTAR (rutas de error)
# El caso exitoso escribe en la Bitacora (MongoDB), que estas pruebas no
# levantan; aqui se verifican las respuestas de error del proceso.

def test_aceptar_solicitud_cuerpo_vacio_400(cliente):
    respuesta = cliente.post(f"{URL}/1/aceptar", {}, format="json")

    assert respuesta.status_code == 400
    assert "id_usuario" in respuesta.json()["errores"]


def test_aceptar_solicitud_inexistente_404(cliente):
    respuesta = cliente.post(
        f"{URL}/999999/aceptar", {"id_usuario": 2}, format="json"
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_aceptar_solicitud_no_pendiente_409(cliente):
    respuesta = cliente.post(
        f"{URL}/3/aceptar", {"id_usuario": 2}, format="json"
    )

    assert respuesta.status_code == 409


def test_aceptar_solicitud_por_usuario_no_propietario_403(cliente):
    # El usuario 4 es beneficiario, no el donante propietario de la donacion 1.
    respuesta = cliente.post(
        f"{URL}/1/aceptar", {"id_usuario": 4}, format="json"
    )

    assert respuesta.status_code == 403