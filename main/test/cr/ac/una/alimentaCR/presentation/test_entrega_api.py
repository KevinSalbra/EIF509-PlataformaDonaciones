"""
Pruebas de integracion de la API de Entrega (/api/v1/entregas).

Usan la base PostgreSQL de Testcontainers con el esquema y los datos de
prueba de Flyway. Cada prueba corre dentro de una transaccion que se
revierte al terminar.

Datos de prueba usados:
- Entrega 1: PENDIENTE (solicitud 3). Donante: organizacion 3 (usuario 3).
  Beneficiaria: organizacion 4 (usuario 4).
- Entrega 2: FINALIZADA (solicitud 5). Donante: organizacion 2 (usuario 2).
  Beneficiaria: organizacion 5 (usuario 5).
- Usuario 5 no participa en la entrega 1.
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import SolicitudService
from cr.ac.una.alimentaCR.data.models import Donacion, Entrega, Solicitud

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/entregas"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


def en_dias(dias):
    return (timezone.now() + timedelta(days=dias)).isoformat()


# ---------------------------------------------------------------- GET

def test_listar_entregas_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.json()) >= 2


def test_obtener_entrega_200(cliente):
    respuesta = cliente.get(f"{URL}/1")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id_entrega"] == 1
    assert cuerpo["id_solicitud"] == 3
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["confirmacion_donante"] is False


def test_obtener_entrega_inexistente_404(cliente):
    respuesta = cliente.get(f"{URL}/999999")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_no_se_puede_crear_una_entrega_por_post_405(cliente):
    respuesta = cliente.post(URL, {}, format="json")

    assert respuesta.status_code == 405
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# -------------------------------------------------------------- PATCH

def test_coordinar_entrega_200_por_el_beneficiario(cliente):
    fecha = en_dias(7)

    respuesta = cliente.patch(
        f"{URL}/1",
        {
            "id_usuario": 4,
            "fecha_acordada": fecha,
            "lugar": "Bodega central",
            "observaciones": "Llevar canastas",
        },
        format="json",
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["lugar"] == "Bodega central"
    assert cuerpo["observaciones"] == "Llevar canastas"
    guardada = Entrega.objects.get(pk=1)
    assert guardada.lugar == "Bodega central"
    assert guardada.fecha_acordada is not None


def test_coordinar_entrega_200_por_el_donante_solo_cambia_lo_enviado(cliente):
    antes = Entrega.objects.get(pk=1)
    observaciones_originales = antes.observaciones

    respuesta = cliente.patch(
        f"{URL}/1",
        {"id_usuario": 3, "lugar": "Nuevo lugar de entrega"},
        format="json",
    )

    assert respuesta.status_code == 200
    despues = Entrega.objects.get(pk=1)
    assert despues.lugar == "Nuevo lugar de entrega"
    assert despues.observaciones == observaciones_originales


def test_coordinar_entrega_sin_campos_de_coordinacion_400(cliente):
    respuesta = cliente.patch(f"{URL}/1", {"id_usuario": 4}, format="json")

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "non_field_errors" in respuesta.json()["errores"]


def test_coordinar_entrega_sin_usuario_400(cliente):
    respuesta = cliente.patch(f"{URL}/1", {"lugar": "Algun lugar"}, format="json")

    assert respuesta.status_code == 400
    assert "id_usuario" in respuesta.json()["errores"]


def test_coordinar_entrega_fecha_con_formato_invalido_400(cliente):
    respuesta = cliente.patch(
        f"{URL}/1",
        {"id_usuario": 4, "fecha_acordada": "pronto"},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "fecha_acordada" in respuesta.json()["errores"]


def test_coordinar_entrega_lugar_vacio_400(cliente):
    respuesta = cliente.patch(
        f"{URL}/1", {"id_usuario": 4, "lugar": "   "}, format="json"
    )

    assert respuesta.status_code == 400
    assert "lugar" in respuesta.json()["errores"]


def test_coordinar_entrega_inexistente_404(cliente):
    respuesta = cliente.patch(
        f"{URL}/999999", {"id_usuario": 4, "lugar": "X"}, format="json"
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_coordinar_entrega_usuario_inexistente_404(cliente):
    respuesta = cliente.patch(
        f"{URL}/1", {"id_usuario": 999999, "lugar": "X"}, format="json"
    )

    assert respuesta.status_code == 404


def test_coordinar_entrega_de_organizacion_no_involucrada_403(cliente):
    respuesta = cliente.patch(
        f"{URL}/1", {"id_usuario": 5, "lugar": "Intruso"}, format="json"
    )

    assert respuesta.status_code == 403
    assert Entrega.objects.get(pk=1).lugar != "Intruso"


def test_coordinar_entrega_finalizada_409(cliente):
    # La entrega 2 esta FINALIZADA; el usuario 2 es el donante involucrado.
    respuesta = cliente.patch(
        f"{URL}/2", {"id_usuario": 2, "lugar": "Otro lugar"}, format="json"
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_coordinar_entrega_con_fecha_pasada_422(cliente):
    respuesta = cliente.patch(
        f"{URL}/1",
        {"id_usuario": 4, "fecha_acordada": en_dias(-1)},
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# --------------------------- ACEPTAR SOLICITUD -> genera una entrega

def test_aceptar_solicitud_201_con_location_hacia_la_entrega(
    cliente, monkeypatch
):
    # El registro en la Bitacora (MongoDB) no forma parte de esta prueba.
    monkeypatch.setattr(
        SolicitudService,
        "_registrar_evento_bitacora",
        lambda self, entrega, id_usuario: None,
    )

    # El usuario 2 es el donante propietario de la donacion 1.
    respuesta = cliente.post(
        "/api/v1/solicitudes/1/aceptar", {"id_usuario": 2}, format="json"
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id_solicitud"] == 1
    assert cuerpo["estado"] == "PENDIENTE"
    assert respuesta["Location"].endswith(f"{URL}/{cuerpo['id_entrega']}")

    # La Location apunta a la entrega recien creada.
    assert cliente.get(respuesta["Location"]).status_code == 200

    # Efectos del proceso: solicitud aceptada, otras rechazadas, donacion asignada.
    assert Solicitud.objects.get(pk=1).estado == "ACEPTADA"
    assert Solicitud.objects.get(pk=2).estado == "RECHAZADA"
    assert Donacion.objects.get(pk=1).estado == "ASIGNADA"