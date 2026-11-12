"""
Configuracion de seguridad (Laboratorio 7, OWASP A02/A05/A07/A10):
cabeceras, rutas sin uso, errores sin detalles internos y tokens.
"""
from datetime import timedelta
from unittest.mock import patch

import jwt
import pytest
from django.conf import settings
from django.test import Client, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import (
    AuthService,
    EntregaService,
)


def test_la_ruta_admin_de_django_no_existe():
    # A02: no se expone una consola de administracion sin uso.
    assert Client().get("/admin/").status_code == 404


def test_http_se_redirige_a_https_en_produccion():
    with override_settings(SECURE_SSL_REDIRECT=True, ALLOWED_HOSTS=["testserver"]):
        respuesta = Client().get("/api/v1/salud")

    assert respuesta.status_code == 301
    assert respuesta["Location"].startswith("https://")


def test_https_incluye_hsts_nosniff_y_frame_options():
    with override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_HSTS_SECONDS=31536000,
        ALLOWED_HOSTS=["testserver"],
    ):
        respuesta = Client().get("/api/v1/salud", secure=True)

    assert respuesta.status_code == 200
    assert respuesta["Strict-Transport-Security"].startswith("max-age=31536000")
    assert respuesta["X-Content-Type-Options"] == "nosniff"
    assert respuesta["X-Frame-Options"] == "DENY"


def test_el_health_check_no_se_redirige_para_la_plataforma():
    # El health check interno de Render usa http: no debe recibir 301.
    with override_settings(SECURE_SSL_REDIRECT=True, ALLOWED_HOSTS=["testserver"]):
        respuesta = Client().get("/actuator/health")

    assert respuesta.status_code != 301


def test_las_cookies_de_sesion_y_csrf_son_seguras_fuera_de_desarrollo():
    if settings.DEBUG:
        pytest.skip("Solo aplica con DEBUG=False (produccion y CI).")
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SESSION_COOKIE_HTTPONLY is True


def test_cors_no_permite_todos_los_origenes():
    assert not getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False)
    assert "*" not in settings.CORS_ALLOWED_ORIGINS


def test_el_token_incluye_expiracion_y_se_rechaza_vencido():
    class Usuario:
        id_usuario = 1
        rol = "ADMINISTRADOR"
        organizacion_id = 1

    token = AuthService.generar_token(Usuario())
    datos = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert datos["exp"] - datos["iat"] <= 3600  # a lo sumo 1 hora

    vencido = jwt.encode(
        {"sub": "1", "exp": timezone.now() - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {vencido}")
    assert cliente.get("/api/v1/solicitudes").status_code == 401


def test_un_token_sin_firma_valida_se_rechaza():
    falso = jwt.encode({"sub": "1"}, "otra-clave", algorithm="HS256")
    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {falso}")

    assert cliente.get("/api/v1/solicitudes").status_code == 401


@pytest.mark.django_db
@pytest.mark.usefixtures("preparar_esquema_flyway")
def test_un_error_inesperado_no_envia_la_traza_al_cliente(escenario_entrega):
    # A10: el cliente recibe Problem Details generico; el detalle va al log.
    cliente = APIClient()
    cliente.credentials(
        HTTP_AUTHORIZATION="Bearer "
        + AuthService.generar_token(escenario_entrega.usuario_donante)
    )
    with patch.object(
        EntregaService,
        "obtener_entrega",
        side_effect=RuntimeError("psycopg.errors.UniqueViolation uk_secreto"),
    ):
        respuesta = cliente.get(f"/api/v1/entregas/{escenario_entrega.entrega.pk}")

    assert respuesta.status_code == 500
    assert respuesta["Content-Type"] == "application/problem+json"
    texto = respuesta.content.decode()
    assert "uk_secreto" not in texto
    assert "Traceback" not in texto 