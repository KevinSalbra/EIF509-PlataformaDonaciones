"""
Pruebas de integracion de la API de Usuario (/api/v1/usuarios).

Datos de prueba usados:
- Usuario 1: ADMINISTRADOR (organizacion 1)
- Usuario 2: REPRESENTANTE_DONANTE (organizacion 2, tipo DONANTE)
- Organizacion 4: tipo BENEFICIARIA
"""

import pytest
from django.contrib.auth.hashers import check_password
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Usuario


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/usuarios"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


@pytest.fixture
def usuario_administrador():
    return Usuario.objects.get(pk=1)


@pytest.fixture
def usuario_donante():
    return Usuario.objects.get(pk=2)


def autenticar_cliente(cliente, usuario):
    token = AuthService.generar_token(usuario)

    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )


def cuerpo_valido(**cambios):
    datos = {
        "id_organizacion": 2,
        "nombre": "Ana Mora",
        "correo": "ana.mora@prueba.com",
        "contrasena": "ClaveSegura123",
        "telefono": "8800-1111",
        "rol": "REPRESENTANTE_DONANTE",
    }

    datos.update(cambios)

    return datos


# ----------------------------------------------------------------
# GET
# ----------------------------------------------------------------

def test_listar_usuarios_200_sin_exponer_contrasena(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()

    assert cuerpo["count"] >= 6

    for usuario in cuerpo["results"]:
        assert "contrasena" not in usuario


def test_obtener_usuario_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(f"{URL}/2")

    assert respuesta.status_code == 200
    assert respuesta.json()["id_usuario"] == 2
    assert (
        respuesta.json()["rol"]
        == "REPRESENTANTE_DONANTE"
    )
    assert "contrasena" not in respuesta.json()


def test_obtener_usuario_inexistente_404(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(
        f"{URL}/999999"
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 404


# ----------------------------------------------------------------
# POST
# ----------------------------------------------------------------

def test_crear_usuario_201_con_location(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    assert respuesta.status_code == 201

    cuerpo = respuesta.json()

    assert cuerpo["estado"] == "ACTIVO"
    assert "contrasena" not in cuerpo

    assert respuesta["Location"].endswith(
        f"{URL}/{cuerpo['id_usuario']}"
    )

    # La contrasena se guarda como hash,
    # no en texto plano.
    guardado = Usuario.objects.get(
        pk=cuerpo["id_usuario"]
    )

    assert (
        guardado.contrasena
        != "ClaveSegura123"
    )

    assert check_password(
        "ClaveSegura123",
        guardado.contrasena,
    )


def test_crear_usuario_y_consultarlo_con_el_location(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    creado = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    consulta = cliente.get(
        creado["Location"]
    )

    assert consulta.status_code == 200

    assert (
        consulta.json()["correo"]
        == "ana.mora@prueba.com"
    )


def test_crear_usuario_cuerpo_vacio_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        {},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA

    errores = respuesta.json()["errores"]

    for campo in (
        "id_organizacion",
        "nombre",
        "correo",
        "contrasena",
        "rol",
    ):
        assert campo in errores


def test_crear_usuario_correo_y_contrasena_invalidos_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            correo="no-es-un-correo",
            contrasena="corta",
        ),
        format="json",
    )

    assert respuesta.status_code == 400

    errores = respuesta.json()["errores"]

    assert "correo" in errores
    assert "contrasena" in errores


def test_crear_usuario_organizacion_inexistente_404(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            id_organizacion=999999
        ),
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_usuario_correo_repetido_409(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    correo_existente = Usuario.objects.get(
        pk=1
    ).correo

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            correo=correo_existente
        ),
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_crear_usuario_rol_incompatible_con_organizacion_422(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    # La organizacion 4 es BENEFICIARIA:
    # no admite un representante donante.
    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            id_organizacion=4,
            rol="REPRESENTANTE_DONANTE",
        ),
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# PUT
# ----------------------------------------------------------------

def test_actualizar_usuario_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.put(
        f"{URL}/2",
        {
            "nombre": "Laura Actualizada",
            "telefono": "8800-9999",
            "rol": "REPRESENTANTE_DONANTE",
            "estado": "INACTIVO",
        },
        format="json",
    )

    assert respuesta.status_code == 200

    assert (
        respuesta.json()["nombre"]
        == "Laura Actualizada"
    )

    assert (
        respuesta.json()["estado"]
        == "INACTIVO"
    )

    assert (
        Usuario.objects.get(pk=2).estado
        == "INACTIVO"
    )


def test_actualizar_usuario_estado_invalido_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.put(
        f"{URL}/2",
        {
            "nombre": "Laura",
            "rol": "REPRESENTANTE_DONANTE",
            "estado": "XX",
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "estado" in respuesta.json()["errores"]


def test_actualizar_usuario_inexistente_404(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.put(
        f"{URL}/999999",
        {
            "nombre": "X",
            "rol": "ADMINISTRADOR",
            "estado": "ACTIVO",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_actualizar_usuario_rol_incompatible_422(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    # El usuario 2 pertenece a una
    # organizacion DONANTE.
    respuesta = cliente.put(
        f"{URL}/2",
        {
            "nombre": "Laura",
            "rol": "REPRESENTANTE_BENEFICIARIA",
            "estado": "ACTIVO",
        },
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# SEGURIDAD
# ----------------------------------------------------------------

def test_usuarios_sin_token_401(
    cliente,
):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_usuarios_con_rol_no_autorizado_403(
    cliente,
    usuario_donante,
):
    autenticar_cliente(
        cliente,
        usuario_donante,
    )

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 403