"""
Pruebas de integracion de la API de Categoria
(/api/v1/categorias).

Datos de prueba usados:
- Categoria 1: Frutas y verduras, ACTIVA
- Categoria 2: Panaderia, ACTIVA
- Categoria 6: Bebidas, INACTIVA
- Usuario 1: ADMINISTRADOR
- Usuario 2: REPRESENTANTE_DONANTE
"""

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Categoria, Usuario


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/categorias"
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
        "nombre": "Productos congelados",
        "descripcion": (
            "Alimentos conservados mediante congelacion."
        ),
    }

    datos.update(cambios)

    return datos


# ----------------------------------------------------------------
# GET
# ----------------------------------------------------------------

def test_listar_categorias_200(
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


def test_obtener_categoria_200(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get(f"{URL}/1")

    assert respuesta.status_code == 200
    assert respuesta.json()["id_categoria"] == 1
    assert respuesta.json()["nombre"] == "Frutas y verduras"
    assert respuesta.json()["estado"] == "ACTIVA"


def test_obtener_categoria_inexistente_404(
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

def test_crear_categoria_201_con_location(
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


def test_crear_categoria_y_consultarla_con_location(
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
        consulta.json()["nombre"]
        == "Productos congelados"
    )


def test_crear_categoria_cuerpo_vacio_400(
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
    assert "nombre" in respuesta.json()["errores"]


def test_crear_categoria_nombre_vacio_400(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.post(
        URL,
        cuerpo_valido(nombre=""),
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "nombre" in respuesta.json()["errores"]


def test_crear_categoria_nombre_duplicado_409(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

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
    assert respuesta["Content-Type"].startswith(
        TIPO_PROBLEMA
    )
    assert respuesta.data["status"] == 409


# ----------------------------------------------------------------
# PUT
# ----------------------------------------------------------------

def test_actualizar_categoria_200(
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
            "nombre": "Bebidas actualizadas",
            "descripcion": "Categoria actualizada.",
            "estado": "ACTIVA",
        },
        format="json",
    )

    assert respuesta.status_code == 200
    assert (
        respuesta.json()["nombre"]
        == "Bebidas actualizadas"
    )
    assert respuesta.json()["estado"] == "ACTIVA"

    guardada = Categoria.objects.get(pk=6)

    assert guardada.nombre == "Bebidas actualizadas"
    assert guardada.estado == "ACTIVA"


def test_actualizar_categoria_estado_invalido_400(
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
            "nombre": "Bebidas",
            "descripcion": "Bebidas para donacion.",
            "estado": "ESTADO_INVALIDO",
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "estado" in respuesta.json()["errores"]


def test_actualizar_categoria_inexistente_404(
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
            "nombre": "Categoria inexistente",
            "descripcion": "Prueba.",
            "estado": "ACTIVA",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"] == TIPO_PROBLEMA


def test_actualizar_categoria_nombre_duplicado_409(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

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
    assert respuesta["Content-Type"].startswith(
        TIPO_PROBLEMA
    )
    assert respuesta.data["status"] == 409


# ----------------------------------------------------------------
# SEGURIDAD
# ----------------------------------------------------------------

def test_categorias_sin_token_401(
    cliente,
):
    respuesta = cliente.get(URL)

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_categorias_con_rol_no_autorizado_403(
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