from datetime import timedelta

import jwt
import pytest
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Usuario


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

URL = "/api/v1/auth/login"
TIPO_PROBLEMA = "application/problem+json"

CORREO = "login.prueba@alimentacr.test"
CONTRASENA = "ClaveSegura123"


@pytest.fixture
def cliente():
    return APIClient()


@pytest.fixture
def usuario_login():
    usuario = Usuario.objects.get(pk=2)

    usuario.correo = CORREO
    usuario.contrasena = make_password(CONTRASENA)
    usuario.estado = Usuario.Estado.ACTIVO
    usuario.save(
        update_fields=[
            "correo",
            "contrasena",
            "estado",
        ]
    )

    return usuario


@pytest.fixture
def usuario_administrador():
    return Usuario.objects.get(pk=1)


@pytest.fixture
def usuario_donante():
    return Usuario.objects.get(pk=2)


@pytest.fixture
def usuario_beneficiario():
    return Usuario.objects.get(pk=4)


def credenciales(**cambios):
    datos = {
        "correo": CORREO,
        "contrasena": CONTRASENA,
    }
    datos.update(cambios)
    return datos


def autenticar_cliente(cliente, usuario):
    token = AuthService.generar_token(usuario)

    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    return cliente


# ------------------------------------------------------------------
# Login
# ------------------------------------------------------------------

def test_login_correcto_200_devuelve_jwt(cliente, usuario_login):
    respuesta = cliente.post(
        URL,
        credenciales(),
        format="json",
    )

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()

    assert "access_token" in cuerpo
    assert cuerpo["token_type"] == "Bearer"

    payload = jwt.decode(
        cuerpo["access_token"],
        settings.SECRET_KEY,
        algorithms=["HS256"],
    )

    assert payload["sub"] == str(usuario_login.id_usuario)
    assert payload["rol"] == usuario_login.rol
    assert payload["id_organizacion"] == usuario_login.organizacion_id
    assert "iat" in payload
    assert "exp" in payload


def test_login_contrasena_incorrecta_401(cliente, usuario_login):
    respuesta = cliente.post(
        URL,
        credenciales(contrasena="ClaveIncorrecta123"),
        format="json",
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Credenciales invalidas."


def test_login_correo_inexistente_401(cliente):
    respuesta = cliente.post(
        URL,
        {
            "correo": "noexiste@alimentacr.test",
            "contrasena": CONTRASENA,
        },
        format="json",
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Credenciales invalidas."


def test_login_usuario_inactivo_401(cliente, usuario_login):
    usuario_login.estado = Usuario.Estado.INACTIVO
    usuario_login.save(update_fields=["estado"])

    respuesta = cliente.post(
        URL,
        credenciales(),
        format="json",
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Credenciales invalidas."


def test_login_cuerpo_vacio_400(cliente):
    respuesta = cliente.post(
        URL,
        {},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA

    errores = respuesta.json()["errores"]

    assert "correo" in errores
    assert "contrasena" in errores


def test_login_correo_invalido_400(cliente):
    respuesta = cliente.post(
        URL,
        {
            "correo": "correo-invalido",
            "contrasena": CONTRASENA,
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert "correo" in respuesta.json()["errores"]


# ------------------------------------------------------------------
# Autenticacion JWT
# ------------------------------------------------------------------

def test_token_valido_identifica_usuario(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(
        cliente,
        usuario_administrador,
    )

    respuesta = cliente.get("/api/v1/usuarios/2")

    assert respuesta.status_code == 200


def test_token_invalido_devuelve_401(cliente):
    cliente.credentials(
        HTTP_AUTHORIZATION="Bearer token-invalido"
    )

    respuesta = cliente.get("/api/v1/usuarios/2")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_token_expirado_devuelve_401(cliente, usuario_login):
    token = jwt.encode(
        {
            "sub": str(usuario_login.id_usuario),
            "rol": usuario_login.rol,
            "id_organizacion": usuario_login.organizacion_id,
            "iat": timezone.now() - timedelta(hours=2),
            "exp": timezone.now() - timedelta(hours=1),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    respuesta = cliente.get("/api/v1/usuarios/2")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_encabezado_authorization_invalido_devuelve_401(cliente):
    cliente.credentials(
        HTTP_AUTHORIZATION="Token abc123"
    )

    respuesta = cliente.get("/api/v1/usuarios/2")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


# ------------------------------------------------------------------
# Autorizacion por rol - endpoints administrativos
# ------------------------------------------------------------------

def test_endpoint_administrativo_sin_token_devuelve_401(cliente):
    respuesta = cliente.get("/api/v1/categorias")

    assert respuesta.status_code == 401
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 401


def test_endpoint_administrativo_donante_devuelve_403(
    cliente,
    usuario_donante,
):
    autenticar_cliente(cliente, usuario_donante)

    respuesta = cliente.get("/api/v1/categorias")

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 403


def test_endpoint_administrativo_beneficiario_devuelve_403(
    cliente,
    usuario_beneficiario,
):
    autenticar_cliente(cliente, usuario_beneficiario)

    respuesta = cliente.get("/api/v1/categorias")

    assert respuesta.status_code == 403
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    assert respuesta.json()["status"] == 403


def test_endpoint_administrativo_administrador_permitido(
    cliente,
    usuario_administrador,
):
    autenticar_cliente(cliente, usuario_administrador)

    respuesta = cliente.get("/api/v1/categorias")

    assert respuesta.status_code == 200