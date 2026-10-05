"""
Pruebas de integracion de la API de Organizacion
(/api/v1/organizaciones).

Datos de prueba usados:
- Organizacion 2: DONANTE, APROBADA
- Organizacion 4: BENEFICIARIA, APROBADA
- Organizacion 6: BENEFICIARIA, PENDIENTE
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.data.models import Organizacion


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/organizaciones"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


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


# ---------------------------------------------------------------- GET

def test_listar_organizaciones_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json()["count"] >= 6


def test_obtener_organizacion_200(cliente):
    respuesta = cliente.get(f"{URL}/2")

    assert respuesta.status_code == 200
    assert respuesta.json()["id_organizacion"] == 2
    assert respuesta.json()["tipo"] == "DONANTE"
    assert respuesta.json()["estado"] == "APROBADA"


def test_obtener_organizacion_inexistente_404(cliente):
    respuesta = cliente.get(f"{URL}/999999")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 404


# --------------------------------------------------------------- POST

def test_crear_organizacion_201_con_location(cliente):
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
    assert guardada.cedula_juridica == "3-101-999999"


def test_crear_organizacion_y_consultarla_con_location(cliente):
    creada = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    consulta = cliente.get(creada["Location"])

    assert consulta.status_code == 200
    assert (
        consulta.json()["cedula_juridica"]
        == "3-101-999999"
    )


def test_crear_organizacion_cuerpo_vacio_400(cliente):
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


def test_crear_organizacion_tipo_invalido_400(cliente):
    respuesta = cliente.post(
        URL,
        cuerpo_valido(tipo="OTRO"),
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "tipo" in respuesta.json()["errores"]


# ---------------------------------------------------------------- PUT

def test_actualizar_organizacion_200(cliente):
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
    assert respuesta.json()["nombre"] == (
        "Asociacion Ayuda Actualizada"
    )
    assert respuesta.json()["estado"] == "APROBADA"

    guardada = Organizacion.objects.get(pk=6)

    assert guardada.nombre == "Asociacion Ayuda Actualizada"
    assert guardada.estado == "APROBADA"


def test_actualizar_organizacion_estado_invalido_400(cliente):
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


def test_actualizar_organizacion_inexistente_404(cliente):
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

def test_crear_organizacion_cedula_juridica_duplicada_409(
    cliente,
):
    organizacion_existente = Organizacion.objects.get(
        id_organizacion=1
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            cedula_juridica=organizacion_existente.cedula_juridica
        ),
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 409