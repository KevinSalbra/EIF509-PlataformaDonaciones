import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.data.models import Donacion


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/donaciones"
URL_PUBLICAR = "/api/v1/donaciones/publicar"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


def cuerpo_valido(**cambios):
    datos = {
        "id_organizacion": 2,
        "id_categoria": 1,
        "alimento": "Tomates",
        "descripcion": "Tomates frescos para donar",
        "cantidad": "15.00",
        "unidad_medida": "KILOGRAMO",
        "fecha_limite_retiro": "2099-12-31",
    }

    datos.update(cambios)
    return datos


# ----------------------------------------------------------------
# GET
# ----------------------------------------------------------------

def test_listar_donaciones_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert isinstance(respuesta.data, list)
    assert len(respuesta.data) >= 6


def test_obtener_donacion_200(cliente):
    respuesta = cliente.get(f"{URL}/1")

    assert respuesta.status_code == 200
    assert respuesta.data["id_donacion"] == 1
    assert respuesta.data["id_organizacion"] == 2
    assert respuesta.data["id_categoria"] == 1
    assert respuesta.data["alimento"] == "Manzanas"
    assert respuesta.data["estado"] == "DISPONIBLE"


def test_obtener_donacion_inexistente_404(cliente):
    respuesta = cliente.get(f"{URL}/999999")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 404
    assert respuesta.data["instance"] == f"{URL}/999999"


# ----------------------------------------------------------------
# POST /publicar
# ----------------------------------------------------------------

def test_publicar_donacion_201_con_location(
    cliente,
    monkeypatch,
):
    monkeypatch.setattr(
        "cr.ac.una.alimentaCR.data.repositories."
        "bitacora_repository.BitacoraRepository.registrar",
        lambda self, evento: None,
    )

    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(),
        format="json",
    )

    assert respuesta.status_code == 201
    assert "Location" in respuesta

    id_donacion = respuesta.data["id_donacion"]

    assert respuesta.data["estado"] == "DISPONIBLE"
    assert respuesta.data["id_organizacion"] == 2
    assert respuesta.data["id_categoria"] == 1
    assert respuesta.data["alimento"] == "Tomates"

    assert Donacion.objects.filter(
        id_donacion=id_donacion
    ).exists()


def test_publicar_donacion_y_consultarla_con_location(
    cliente,
    monkeypatch,
):
    monkeypatch.setattr(
        "cr.ac.una.alimentaCR.data.repositories."
        "bitacora_repository.BitacoraRepository.registrar",
        lambda self, evento: None,
    )

    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(),
        format="json",
    )

    assert respuesta.status_code == 201

    location = respuesta["Location"]

    respuesta_consulta = cliente.get(location)

    assert respuesta_consulta.status_code == 200
    assert (
        respuesta_consulta.data["id_donacion"]
        == respuesta.data["id_donacion"]
    )


def test_publicar_donacion_cuerpo_vacio_400(cliente):
    respuesta = cliente.post(
        URL_PUBLICAR,
        {},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 400
    assert "errores" in respuesta.data


def test_publicar_donacion_unidad_invalida_400(cliente):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            unidad_medida="SACO"
        ),
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert "unidad_medida" in respuesta.data["errores"]


def test_publicar_donacion_organizacion_inexistente_404(
    cliente,
):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            id_organizacion=999999
        ),
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 404


def test_publicar_donacion_categoria_inexistente_404(
    cliente,
):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            id_categoria=999999
        ),
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 404


def test_publicar_donacion_categoria_inactiva_422(
    cliente,
):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            id_categoria=6
        ),
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 422


def test_publicar_donacion_cantidad_invalida_422(
    cliente,
):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            cantidad="0.00"
        ),
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 422


def test_publicar_donacion_organizacion_no_autorizada_422(
    cliente,
):
    respuesta = cliente.post(
        URL_PUBLICAR,
        cuerpo_valido(
            id_organizacion=4
        ),
        format="json",
    )

    assert respuesta.status_code == 422
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 422