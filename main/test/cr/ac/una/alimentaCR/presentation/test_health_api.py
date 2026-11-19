"""
/actuator/health (Laboratorio 7): la plataforma lo usa para saber si el
despliegue funciono. Responde solo UP/DOWN, sin detalles internos.
"""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.presentation.views import VistaHealth

URL = "/actuator/health"

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]


@pytest.fixture
def cliente():
    return APIClient()


def test_health_up_cuando_las_bases_responden(cliente):
    with patch.object(VistaHealth, "_mongo_disponible", return_value=True):
        respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "UP"}


def test_health_no_requiere_autenticacion(cliente):
    with patch.object(VistaHealth, "_mongo_disponible", return_value=True):
        respuesta = cliente.get(URL)  # sin token

    assert respuesta.status_code == 200


def test_health_down_503_si_mongodb_no_responde(cliente):
    with patch.object(VistaHealth, "_mongo_disponible", return_value=False):
        respuesta = cliente.get(URL)

    assert respuesta.status_code == 503
    assert respuesta.json() == {"status": "DOWN"}


def test_health_down_503_si_postgresql_no_responde(cliente):
    with patch.object(
        VistaHealth, "_postgres_disponible", return_value=False
    ), patch.object(VistaHealth, "_mongo_disponible", return_value=True):
        respuesta = cliente.get(URL)

    assert respuesta.status_code == 503
    assert respuesta.json() == {"status": "DOWN"}


def test_health_no_revela_detalles_ni_credenciales(cliente):
    with patch.object(VistaHealth, "_mongo_disponible", return_value=False):
        texto = cliente.get(URL).content.decode().lower()

    for secreto in ("mongo", "postgres", "password", "host", "traceback"):
        assert secreto not in texto


def test_el_fallo_de_una_base_se_escribe_en_el_registro_no_en_la_respuesta(
    cliente, caplog
):
    with patch(
        "cr.ac.una.alimentaCR.presentation.views.obtener_cliente_mongo",
        side_effect=RuntimeError("conexion rechazada"),
    ):
        respuesta = cliente.get(URL)

    assert respuesta.status_code == 503
    assert "conexion rechazada" not in respuesta.content.decode()
    assert "MongoDB no responde" in caplog.text