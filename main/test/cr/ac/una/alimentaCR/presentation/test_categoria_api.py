"""
Pruebas de integracion de la API de Categoria
(/api/v1/categorias).

Datos de prueba usados:
- Categoria 1: Frutas y verduras, ACTIVA
- Categoria 2: Panaderia, ACTIVA
- Categoria 6: Bebidas, INACTIVA
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.data.models import Categoria


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/categorias"
TIPO_PROBLEMA = "application/problem+json"


@pytest.fixture
def cliente():
    return APIClient()


def cuerpo_valido(**cambios):
    datos = {
        "nombre": "Productos congelados",
        "descripcion": "Alimentos conservados mediante congelacion.",
    }
    datos.update(cambios)
    return datos


# ---------------------------------------------------------------- GET

def test_listar_categorias_200(cliente):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.json()["count"] >= 6


def test_obtener_categoria_200(cliente):
    respuesta = cliente.get(f"{URL}/1")

    assert respuesta.status_code == 200
    assert respuesta.json()["id_categoria"] == 1
    assert respuesta.json()["nombre"] == "Frutas y verduras"
    assert respuesta.json()["estado"] == "ACTIVA"


def test_obtener_categoria_inexistente_404(cliente):
    respuesta = cliente.get(f"{URL}/999999")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 404


# --------------------------------------------------------------- POST

def test_crear_categoria_201_con_location(cliente):
    respuesta = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    assert respuesta.status_code == 201

    cuerpo = respuesta.json()

    assert cuerpo["nombre"] == "Productos congelados"
    assert cuerpo["estado"] == "ACTIVA"

    assert respuesta["Location"].endswith(
        f"{URL}/{cuerpo['id_categoria']}"
    )

    guardada = Categoria.objects.get(
        pk=cuerpo["id_categoria"]
    )

    assert guardada.nombre == "Productos congelados"
    assert guardada.estado == "ACTIVA"


def test_crear_categoria_y_consultarla_con_location(cliente):
    creada = cliente.post(
        URL,
        cuerpo_valido(),
        format="json",
    )

    consulta = cliente.get(creada["Location"])

    assert consulta.status_code == 200
    assert consulta.json()["nombre"] == "Productos congelados"


def test_crear_categoria_cuerpo_vacio_400(cliente):
    respuesta = cliente.post(
        URL,
        {},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "nombre" in respuesta.json()["errores"]


def test_crear_categoria_nombre_vacio_400(cliente):
    respuesta = cliente.post(
        URL,
        cuerpo_valido(nombre=""),
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "nombre" in respuesta.json()["errores"]


# ---------------------------------------------------------------- PUT

def test_actualizar_categoria_200(cliente):
    respuesta = cliente.put(
        f"{URL}/6",
        {
            "nombre": "Bebidas actualizadas",
            "descripcion": "Categoria actualizada.",
            "estado": "ACTIVA",
        },
        format="json",
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Bebidas actualizadas"
    assert respuesta.json()["estado"] == "ACTIVA"

    guardada = Categoria.objects.get(pk=6)

    assert guardada.nombre == "Bebidas actualizadas"
    assert guardada.estado == "ACTIVA"


def test_actualizar_categoria_estado_invalido_400(cliente):
    respuesta = cliente.put(
        f"{URL}/6",
        {
            "nombre": "Bebidas",
            "descripcion": "Bebidas para donacion.",
            "estado": "ESTADO_INVALIDO",
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "estado" in respuesta.json()["errores"]


def test_actualizar_categoria_inexistente_404(cliente):
    respuesta = cliente.put(
        f"{URL}/999999",
        {
            "nombre": "Categoria inexistente",
            "descripcion": "Prueba.",
            "estado": "ACTIVA",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA

def test_crear_categoria_nombre_duplicado_409(
    cliente,
):
    categoria_existente = Categoria.objects.get(
        id_categoria=1
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(
            nombre=categoria_existente.nombre
        ),
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 409


def test_actualizar_categoria_nombre_duplicado_409(
    cliente,
):
    categoria_existente = Categoria.objects.get(
        id_categoria=1
    )

    respuesta = cliente.put(
        f"{URL}/2",
        {
            "nombre": categoria_existente.nombre,
            "descripcion": "Descripcion de prueba",
            "estado": "ACTIVA",
        },
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    assert respuesta.data["status"] == 409