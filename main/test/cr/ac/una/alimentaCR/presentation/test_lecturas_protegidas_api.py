"""
Lecturas de solicitudes y entregas: requieren sesion y cada usuario ve
solo lo de su organizacion (el administrador ve todo).

Una organizacion "participa" en una solicitud si es la beneficiaria que
la envio o la donante de la donacion solicitada; en una entrega, si lo
es de su solicitud aceptada. Si un recurso no le corresponde, la API
responde 404 (igual que si no existiera) para no revelar su existencia.

Datos de prueba (Flyway):
- Usuarios: 1 admin, 2 donante org 2, 3 donante org 3,
  4 beneficiaria org 4, 5 beneficiaria org 5.
- Solicitudes (donacion -> donante, beneficiaria):
  1 (d1: org 2, org 4)  2 (d1: org 2, org 5)  3 (d2: org 3, org 4)
  4 (d2: org 3, org 5)  5 (d3: org 2, org 5)  6 (d4: org 2, org 4)
- Entregas: 1 (solicitud 3: donante org 3, beneficiaria org 4)
            2 (solicitud 5: donante org 2, beneficiaria org 5)
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Entrega, Solicitud, Usuario

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

TIPO_PROBLEMA = "application/problem+json"
SOLICITUDES = "/api/v1/solicitudes"
ENTREGAS = "/api/v1/entregas"


@pytest.fixture
def cliente():
    return APIClient()


def autenticar(cliente, id_usuario):
    token = AuthService.generar_token(Usuario.objects.get(pk=id_usuario))
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


def ids(respuesta, campo):
    return {item[campo] for item in respuesta.json()["results"]}


# ---------------------------------------------------------- sin sesion

@pytest.mark.parametrize(
    "ruta",
    [
        SOLICITUDES,
        f"{SOLICITUDES}/1",
        ENTREGAS,
        f"{ENTREGAS}/1",
    ],
)
def test_lecturas_sin_token_devuelven_401(cliente, ruta):
    respuesta = cliente.get(ruta)

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


# --------------------------------------------------- listados por rol

def test_administrador_ve_todas_las_solicitudes_y_entregas(cliente):
    autenticar(cliente, 1)

    solicitudes = cliente.get(SOLICITUDES).json()["count"]
    entregas = cliente.get(ENTREGAS).json()["count"]

    assert solicitudes == Solicitud.objects.count() == 6
    assert entregas == Entrega.objects.count() == 2


@pytest.mark.parametrize(
    "id_usuario, esperadas",
    [
        (4, {1, 3, 6}),   # beneficiaria org 4
        (5, {2, 4, 5}),   # beneficiaria org 5
        (2, {1, 2, 5, 6}),  # donante org 2
        (3, {3, 4}),      # donante org 3
    ],
)
def test_cada_organizacion_ve_solo_sus_solicitudes(
    cliente, id_usuario, esperadas
):
    autenticar(cliente, id_usuario)

    respuesta = cliente.get(SOLICITUDES)

    assert respuesta.status_code == 200
    assert ids(respuesta, "id_solicitud") == esperadas
    assert respuesta.json()["count"] == len(esperadas)


@pytest.mark.parametrize(
    "id_usuario, esperadas",
    [
        (4, {1}),  # beneficiaria de la solicitud 3
        (5, {2}),  # beneficiaria de la solicitud 5
        (2, {2}),  # donante de la donacion 3
        (3, {1}),  # donante de la donacion 2
    ],
)
def test_cada_organizacion_ve_solo_sus_entregas(
    cliente, id_usuario, esperadas
):
    autenticar(cliente, id_usuario)

    respuesta = cliente.get(ENTREGAS)

    assert respuesta.status_code == 200
    assert ids(respuesta, "id_entrega") == esperadas


def test_un_filtro_no_permite_ver_solicitudes_de_otra_organizacion(
    cliente,
):
    autenticar(cliente, 4)

    respuesta = cliente.get(SOLICITUDES, {"id_organizacion": 5})

    assert respuesta.status_code == 200
    assert respuesta.json()["count"] == 0


# ---------------------------------------------------------- detalle

@pytest.mark.parametrize(
    "id_usuario, id_solicitud, codigo",
    [
        (4, 1, 200),  # la envio
        (2, 1, 200),  # es la dueña de la donacion
        (1, 1, 200),  # administrador
        (5, 1, 404),  # otra beneficiaria
        (3, 1, 404),  # otro donante
        (4, 2, 404),  # solicitud de otra beneficiaria
    ],
)
def test_detalle_de_solicitud_segun_la_organizacion(
    cliente, id_usuario, id_solicitud, codigo
):
    autenticar(cliente, id_usuario)

    respuesta = cliente.get(f"{SOLICITUDES}/{id_solicitud}")

    assert respuesta.status_code == codigo
    if codigo == 404:
        assert respuesta["Content-Type"] == TIPO_PROBLEMA


@pytest.mark.parametrize(
    "id_usuario, id_entrega, codigo",
    [
        (4, 1, 200),  # beneficiaria
        (3, 1, 200),  # donante
        (1, 1, 200),  # administrador
        (5, 1, 404),  # no participa
        (2, 1, 404),  # no participa
        (4, 2, 404),
    ],
)
def test_detalle_de_entrega_segun_la_organizacion(
    cliente, id_usuario, id_entrega, codigo
):
    autenticar(cliente, id_usuario)

    respuesta = cliente.get(f"{ENTREGAS}/{id_entrega}")

    assert respuesta.status_code == codigo
    if codigo == 404:
        assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_coordinar_una_entrega_ajena_sigue_dando_403(cliente):
    """La restriccion de lectura no cambia el proceso 5 (PATCH)."""
    autenticar(cliente, 5)

    respuesta = cliente.patch(
        f"{ENTREGAS}/1", {"lugar": "Bodega"}, format="json"
    )

    assert respuesta.status_code == 403