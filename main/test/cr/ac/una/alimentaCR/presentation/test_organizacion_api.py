"""
Pruebas de integracion de la API de Organizacion
(/api/v1/organizaciones).

Datos de prueba usados:
- Organizacion 2: DONANTE, APROBADA
- Organizacion 4: BENEFICIARIA, APROBADA
- Organizacion 6: BENEFICIARIA, PENDIENTE
- Usuario 1: ADMINISTRADOR
- Usuario 2: REPRESENTANTE_DONANTE
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import (
    Organizacion,
    Usuario,
)


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/organizaciones"
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
        "nombre": "Banco de Alimentos Prueba",
        "tipo": "DONANTE",
        "cedula_juridica": "3-101-999999",
        "descripcion": "Organizacion creada para pruebas.",
        "direccion": "Heredia, Costa Rica",
        "telefono": "2200-9999",
    }

    datos.update(cambios)

    return datos


# ----------------------------------------------------------------
# GET
# ----------------------------------------------------------------

def test_listar_organizaciones_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json()["count"] >= 6


def test_obtener_organizacion_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(f"{URL}/2")

    assert respuesta.status_code == 200
    assert respuesta.json()["id_organizacion"] == 2
    assert respuesta.json()["tipo"] == "DONANTE"
    assert respuesta.json()["estado"] == "APROBADA"


def test_obtener_organizacion_inexistente_404(
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

def test_crear_organizacion_201_con_location(
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

    assert cuerpo["nombre"] == "Banco de Alimentos Prueba"
    assert cuerpo["tipo"] == "DONANTE"
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["fecha_registro"] is not None

    assert respuesta["Location"].endswith(
        f"{URL}/{cuerpo['id_organizacion']}"
    )

    guardada = Organizacion.objects.get(
        pk=cuerpo["id_organizacion"]
    )

    assert guardada.estado == "PENDIENTE"
    assert (
        guardada.cedula_juridica
        == "3-101-999999"
    )


def test_crear_organizacion_y_consultarla_con_location(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    creada = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    consulta = cliente.get(
        creada["Location"]
    )

    assert consulta.status_code == 200
    assert (
        consulta.json()["cedula_juridica"]
        == "3-101-999999"
    )


def test_crear_organizacion_cuerpo_vacio_400(
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
        "nombre",
        "tipo",
        "cedula_juridica",
        "direccion",
        "telefono",
    ):
        assert campo in errores


def test_crear_organizacion_tipo_invalido_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(tipo="OTRO"),
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "tipo" in respuesta.json()["errores"]


def test_crear_organizacion_cedula_juridica_duplicada_409(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    organizacion_existente = Organizacion.objects.get(
        id_organizacion=1
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            cedula_juridica=(
                organizacion_existente.cedula_juridica
            )
        ),
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"].startswith(
        TIPO_PROBLEMA
    )
    assert respuesta.data["status"] == 409


# ----------------------------------------------------------------
# PUT
# ----------------------------------------------------------------

def test_actualizar_organizacion_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.put(
        f"{URL}/6",
        {
            "nombre": "Asociacion Ayuda Actualizada",
            "tipo": "BENEFICIARIA",
            "descripcion": "Descripcion actualizada.",
            "direccion": "San Ramon, Costa Rica",
            "telefono": "2200-8888",
            "estado": "APROBADA",
        },
        format="json",
    )

    assert respuesta.status_code == 200

    assert (
        respuesta.json()["nombre"]
        == "Asociacion Ayuda Actualizada"
    )

    assert (
        respuesta.json()["estado"]
        == "APROBADA"
    )

    guardada = Organizacion.objects.get(pk=6)

    assert (
        guardada.nombre
        == "Asociacion Ayuda Actualizada"
    )

    assert guardada.estado == "APROBADA"


def test_actualizar_organizacion_estado_invalido_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.put(
        f"{URL}/6",
        {
            "nombre": "Asociacion Ayuda del Valle",
            "tipo": "BENEFICIARIA",
            "direccion": "San Ramon, Costa Rica",
            "telefono": "2200-0006",
            "estado": "ESTADO_INVALIDO",
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "estado" in respuesta.json()["errores"]


def test_actualizar_organizacion_inexistente_404(
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
            "nombre": "Organizacion Inexistente",
            "tipo": "DONANTE",
            "direccion": "Heredia, Costa Rica",
            "telefono": "2200-1111",
            "estado": "APROBADA",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# ----------------------------------------------------------------
# SEGURIDAD
# ----------------------------------------------------------------

def test_organizaciones_sin_token_401(
    cliente,
):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_organizaciones_con_rol_no_autorizado_403(
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