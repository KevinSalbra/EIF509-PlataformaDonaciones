"""
Pruebas de integracion de paginacion, orden por parametro y filtros de
las colecciones de la API.

Usan la base PostgreSQL de Testcontainers con el esquema y los datos de
prueba de Flyway. Los resultados esperados se calculan con el ORM sobre
la misma base, de modo que las pruebas no dependen de cuantos datos de
prueba existan.
"""

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import (
    Donacion,
    Solicitud,
    Usuario,
)


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]


TIPO_PROBLEMA = "application/problem+json"

METADATOS = {
    "count",
    "page",
    "page_size",
    "total_pages",
    "next",
    "previous",
    "results",
}

ID_POR_COLECCION = {
    "usuarios": "id_usuario",
    "organizaciones": "id_organizacion",
    "categorias": "id_categoria",
    "entregas": "id_entrega",
    "solicitudes": "id_solicitud",
    "donaciones": "id_donacion",
}


@pytest.fixture
def cliente():
    return APIClient()


@pytest.fixture
def cliente_admin():
    cliente = APIClient()

    usuario = Usuario.objects.get(pk=1)
    token = AuthService.generar_token(usuario)

    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    return cliente


def url(coleccion):
    return f"/api/v1/{coleccion}"


def ids_de(respuesta, coleccion):
    campo = ID_POR_COLECCION[coleccion]

    return [
        elemento[campo]
        for elemento in respuesta.json()["results"]
    ]


def crear_donacion(
    dias_para_vencer,
    alimento="Alimento de prueba",
):
    return Donacion.objects.create(
        organizacion_donante_id=2,
        categoria_id=1,
        alimento=alimento,
        cantidad=Decimal("5.00"),
        unidad_medida="KILOGRAMO",
        fecha_publicacion=timezone.now(),
        fecha_limite_retiro=(
            timezone.localdate()
            + timedelta(days=dias_para_vencer)
        ),
        estado="DISPONIBLE",
    )


# ------------------------------------------------------------
# PAGINACION
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "coleccion",
    list(ID_POR_COLECCION),
)
def test_toda_coleccion_devuelve_metadatos_de_paginacion(
    cliente_admin,
    coleccion,
):
    respuesta = cliente_admin.get(
        url(coleccion)
    )

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()

    assert set(cuerpo) == METADATOS
    assert cuerpo["page"] == 1
    assert cuerpo["page_size"] == 10

    assert cuerpo["total_pages"] == max(
        1,
        math.ceil(cuerpo["count"] / 10),
    )

    assert len(cuerpo["results"]) <= 10


def test_page_size_limita_los_resultados_y_ofrece_la_siguiente(
    cliente_admin,
):
    total = Usuario.objects.count()

    cuerpo = cliente_admin.get(
        url("usuarios"),
        {"page_size": 2},
    ).json()

    assert len(cuerpo["results"]) == 2
    assert cuerpo["count"] == total
    assert cuerpo["page_size"] == 2
    assert cuerpo["total_pages"] == math.ceil(total / 2)
    assert cuerpo["previous"] is None
    assert "page=2" in cuerpo["next"]


def test_segunda_pagina_trae_otros_elementos_y_tiene_previous(
    cliente_admin,
):
    primera = cliente_admin.get(
        url("usuarios"),
        {
            "page_size": 2,
            "page": 1,
        },
    )

    segunda = cliente_admin.get(
        url("usuarios"),
        {
            "page_size": 2,
            "page": 2,
        },
    )

    assert segunda.status_code == 200
    assert segunda.json()["page"] == 2
    assert segunda.json()["previous"] is not None

    assert not set(
        ids_de(primera, "usuarios")
    ) & set(
        ids_de(segunda, "usuarios")
    )


def test_la_ultima_pagina_no_tiene_siguiente(
    cliente_admin,
):
    total = Usuario.objects.count()
    ultima = math.ceil(total / 2)

    cuerpo = cliente_admin.get(
        url("usuarios"),
        {
            "page_size": 2,
            "page": ultima,
        },
    ).json()

    assert cuerpo["next"] is None
    assert cuerpo["previous"] is not None


def test_page_size_tiene_un_maximo_de_100(
    cliente_admin,
):
    cuerpo = cliente_admin.get(
        url("usuarios"),
        {"page_size": 1000},
    ).json()

    assert cuerpo["page_size"] == 100


@pytest.mark.parametrize(
    "pagina",
    ["0", "999", "abc"],
)
def test_pagina_invalida_400(
    cliente_admin,
    pagina,
):
    respuesta = cliente_admin.get(
        url("usuarios"),
        {"page": pagina},
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "page" in respuesta.json()["errores"]


# ------------------------------------------------------------
# ORDEN
# ------------------------------------------------------------

def test_orden_descendente_por_id(
    cliente_admin,
):
    esperado = list(
        Usuario.objects.order_by(
            "-id_usuario"
        ).values_list(
            "id_usuario",
            flat=True,
        )
    )

    respuesta = cliente_admin.get(
        url("usuarios"),
        {"ordering": "-id_usuario"},
    )

    assert respuesta.status_code == 200

    assert (
        ids_de(respuesta, "usuarios")
        == esperado
    )


def test_orden_ascendente_por_nombre(
    cliente_admin,
):
    esperado = list(
        Usuario.objects.order_by(
            "nombre",
            "pk",
        ).values_list(
            "id_usuario",
            flat=True,
        )
    )

    respuesta = cliente_admin.get(
        url("usuarios"),
        {"ordering": "nombre"},
    )

    assert (
        ids_de(respuesta, "usuarios")
        == esperado
    )


def test_orden_por_varios_campos(
    cliente,
):
    esperado = list(
        Donacion.objects.order_by(
            "estado",
            "-id_donacion",
        ).values_list(
            "id_donacion",
            flat=True,
        )
    )

    respuesta = cliente.get(
        url("donaciones"),
        {
            "ordering": "estado,-id_donacion",
        },
    )

    assert (
        ids_de(respuesta, "donaciones")
        == esperado
    )


@pytest.mark.parametrize(
    "coleccion, campo",
    [
        (
            "usuarios",
            "contrasena",
        ),
        (
            "usuarios",
            "--id_usuario",
        ),
        (
            "donaciones",
            "organizacion_donante__nombre",
        ),
        (
            "solicitudes",
            "campo_inexistente",
        ),
    ],
)
def test_orden_por_un_campo_no_permitido_400(
    cliente_admin,
    coleccion,
    campo,
):
    respuesta = cliente_admin.get(
        url(coleccion),
        {"ordering": campo},
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "ordering" in respuesta.json()["errores"]


# ------------------------------------------------------------
# FILTROS: DONACIONES
# ------------------------------------------------------------

def test_filtrar_donaciones_por_estado(
    cliente,
):
    esperado = Donacion.objects.filter(
        estado="DISPONIBLE"
    ).count()

    cuerpo = cliente.get(
        url("donaciones"),
        {"estado": "DISPONIBLE"},
    ).json()

    assert cuerpo["count"] == esperado >= 1

    assert all(
        donacion["estado"] == "DISPONIBLE"
        for donacion in cuerpo["results"]
    )


def test_filtrar_donaciones_por_categoria(
    cliente,
):
    categoria = Donacion.objects.get(
        pk=1
    ).categoria_id

    esperado = Donacion.objects.filter(
        categoria_id=categoria
    ).count()

    cuerpo = cliente.get(
        url("donaciones"),
        {"id_categoria": categoria},
    ).json()

    assert cuerpo["count"] == esperado >= 1

    assert all(
        donacion["id_categoria"] == categoria
        for donacion in cuerpo["results"]
    )


def test_filtrar_donaciones_por_organizacion_donante(
    cliente,
):
    esperado = Donacion.objects.filter(
        organizacion_donante_id=2
    ).count()

    cuerpo = cliente.get(
        url("donaciones"),
        {"id_organizacion": 2},
    ).json()

    assert cuerpo["count"] == esperado >= 1

    assert all(
        donacion["id_organizacion"] == 2
        for donacion in cuerpo["results"]
    )


def test_filtrar_donaciones_combinando_filtros(
    cliente,
):
    esperado = Donacion.objects.filter(
        estado="DISPONIBLE",
        organizacion_donante_id=2,
    ).count()

    cuerpo = cliente.get(
        url("donaciones"),
        {
            "estado": "DISPONIBLE",
            "id_organizacion": 2,
        },
    ).json()

    assert cuerpo["count"] == esperado >= 1

    assert all(
        (
            donacion["estado"] == "DISPONIBLE"
            and donacion["id_organizacion"] == 2
        )
        for donacion in cuerpo["results"]
    )


def test_filtrar_donaciones_por_vencer(
    cliente,
):
    por_vencer = crear_donacion(
        dias_para_vencer=3
    )

    lejana = crear_donacion(
        dias_para_vencer=30
    )

    cuerpo = cliente.get(
        url("donaciones"),
        {
            "por_vencer_en_dias": 7,
            "page_size": 100,
        },
    ).json()

    ids = [
        donacion["id_donacion"]
        for donacion in cuerpo["results"]
    ]

    assert por_vencer.id_donacion in ids
    assert lejana.id_donacion not in ids

    hoy = timezone.localdate()

    for donacion in cuerpo["results"]:
        assert donacion["estado"] == "DISPONIBLE"

        limite = date.fromisoformat(
            donacion["fecha_limite_retiro"]
        )

        assert (
            hoy
            <= limite
            <= hoy + timedelta(days=7)
        )


def test_filtrar_ordenar_y_paginar_a_la_vez(
    cliente,
):
    disponibles = Donacion.objects.filter(
        estado="DISPONIBLE"
    )

    mayor_id = (
        disponibles
        .order_by("-id_donacion")
        .first()
        .id_donacion
    )

    cuerpo = cliente.get(
        url("donaciones"),
        {
            "estado": "DISPONIBLE",
            "ordering": "-id_donacion",
            "page_size": 1,
        },
    ).json()

    assert (
        cuerpo["count"]
        == disponibles.count()
    )

    assert len(cuerpo["results"]) == 1

    assert (
        cuerpo["results"][0]["id_donacion"]
        == mayor_id
    )


@pytest.mark.parametrize(
    "parametro, valor",
    [
        (
            "estado",
            "NO_EXISTE",
        ),
        (
            "id_categoria",
            "0",
        ),
        (
            "id_organizacion",
            "abc",
        ),
        (
            "por_vencer_en_dias",
            "0",
        ),
        (
            "por_vencer_en_dias",
            "400",
        ),
    ],
)
def test_filtros_de_donaciones_invalidos_400(
    cliente,
    parametro,
    valor,
):
    respuesta = cliente.get(
        url("donaciones"),
        {parametro: valor},
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert parametro in respuesta.json()["errores"]


# ------------------------------------------------------------
# FILTROS: SOLICITUDES
# ------------------------------------------------------------

def ids_esperados(**filtros):
    return set(
        Solicitud.objects.filter(
            **filtros
        ).values_list(
            "id_solicitud",
            flat=True,
        )
    )


def test_filtrar_solicitudes_por_estado(
    cliente,
):
    respuesta = cliente.get(
        url("solicitudes"),
        {"estado": "PENDIENTE"},
    )

    esperado = ids_esperados(
        estado="PENDIENTE"
    )

    assert esperado

    assert (
        set(ids_de(respuesta, "solicitudes"))
        == esperado
    )


def test_filtrar_solicitudes_por_organizacion_beneficiaria(
    cliente,
):
    respuesta = cliente.get(
        url("solicitudes"),
        {"id_organizacion": 4},
    )

    esperado = ids_esperados(
        organizacion_beneficiaria_id=4
    )

    assert esperado

    assert (
        set(ids_de(respuesta, "solicitudes"))
        == esperado
    )


def test_filtrar_solicitudes_por_donacion(
    cliente,
):
    respuesta = cliente.get(
        url("solicitudes"),
        {"id_donacion": 2},
    )

    esperado = ids_esperados(
        donacion_id=2
    )

    assert esperado

    assert (
        set(ids_de(respuesta, "solicitudes"))
        == esperado
    )


def test_filtrar_solicitudes_combinando_filtros(
    cliente,
):
    respuesta = cliente.get(
        url("solicitudes"),
        {
            "estado": "ACEPTADA",
            "id_organizacion": 5,
        },
    )

    esperado = ids_esperados(
        estado="ACEPTADA",
        organizacion_beneficiaria_id=5,
    )

    assert esperado

    assert (
        set(ids_de(respuesta, "solicitudes"))
        == esperado
    )


@pytest.mark.parametrize(
    "parametro, valor",
    [
        (
            "estado",
            "NO_EXISTE",
        ),
        (
            "id_organizacion",
            "0",
        ),
        (
            "id_donacion",
            "abc",
        ),
    ],
)
def test_filtros_de_solicitudes_invalidos_400(
    cliente,
    parametro,
    valor,
):
    respuesta = cliente.get(
        url("solicitudes"),
        {parametro: valor},
    )

    assert respuesta.status_code == 400
    assert parametro in respuesta.json()["errores"]