"""
Registros estructurados (JSON) y eventos de seguridad (Laboratorio 7,
OWASP A09). Nunca se registran contrasenas ni tokens.
"""
import json
import logging
import sys

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.config.logging_json import JsonFormatter
from cr.ac.una.alimentaCR.data.models import Usuario


def registro(mensaje="hola", nivel=logging.INFO, extra=None, exc_info=None):
    return logging.LogRecord(
        "prueba", nivel, __file__, 1, mensaje, (), exc_info
    ), extra


def formatear(mensaje="hola", nivel=logging.INFO, extra=None, exc_info=None):
    r = logging.LogRecord("prueba", nivel, __file__, 1, mensaje, (), exc_info)
    for clave, valor in (extra or {}).items():
        setattr(r, clave, valor)
    return json.loads(JsonFormatter().format(r))


# ---------------------------------------------------------------- formato

def test_cada_registro_es_un_objeto_json_con_los_campos_basicos():
    linea = formatear("Inicio", logging.WARNING)

    assert linea["level"] == "WARNING"
    assert linea["logger"] == "prueba"
    assert linea["message"] == "Inicio"
    assert linea["timestamp"].endswith("+00:00")


def test_los_campos_extra_se_incluyen_para_poder_filtrarlos():
    linea = formatear(extra={"evento": "login_fallido", "ip": "10.0.0.1"})

    assert linea["evento"] == "login_fallido"
    assert linea["ip"] == "10.0.0.1"


@pytest.mark.parametrize(
    "campo", ["password", "contrasena", "token", "authorization", "secret_key"]
)
def test_los_campos_con_nombre_sensible_se_enmascaran(campo):
    linea = formatear(extra={campo: "valor-secreto"})

    assert linea[campo] == "***"
    assert "valor-secreto" not in json.dumps(linea)


def test_una_excepcion_se_registra_como_texto_en_el_campo_exception():
    try:
        raise ValueError("fallo de prueba")
    except ValueError:
        linea = formatear("Error", logging.ERROR, exc_info=sys.exc_info())

    assert "ValueError: fallo de prueba" in linea["exception"]


def test_el_mensaje_se_formatea_en_una_sola_linea_json():
    texto = JsonFormatter().format(
        logging.LogRecord("p", logging.INFO, __file__, 1, "a %s", ("b",), None)
    )

    assert "\n" not in texto
    assert json.loads(texto)["message"] == "a b"


# ------------------------------------------------- eventos de seguridad

pytestmark_db = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]


@pytest.fixture
def usuario_con_clave(escenario_entrega):
    usuario = escenario_entrega.usuario_donante
    usuario.contrasena = make_password("Clave-correcta-1")
    usuario.save()
    return usuario


@pytest.mark.django_db
def test_login_fallido_registra_el_evento_sin_la_contrasena(
    usuario_con_clave, caplog
):
    cliente = APIClient()

    with caplog.at_level(logging.WARNING, logger="seguridad"):
        respuesta = cliente.post(
            "/api/v1/auth/login",
            {"correo": usuario_con_clave.correo, "contrasena": "equivocada-99"},
            format="json",
        )

    assert respuesta.status_code == 401
    eventos = [r for r in caplog.records if r.name == "seguridad"]
    assert len(eventos) >= 1
    assert eventos[0].evento == "login_fallido"
    assert eventos[0].correo == usuario_con_clave.correo
    assert "equivocada-99" not in caplog.text


@pytest.mark.django_db
def test_login_correcto_no_registra_evento_de_fallo(usuario_con_clave, caplog):
    with caplog.at_level(logging.WARNING, logger="seguridad"):
        respuesta = APIClient().post(
            "/api/v1/auth/login",
            {"correo": usuario_con_clave.correo, "contrasena": "Clave-correcta-1"},
            format="json",
        )

    assert respuesta.status_code == 200
    assert [r for r in caplog.records if r.name == "seguridad"] == []


@pytest.mark.django_db
def test_acceso_sin_token_registra_acceso_denegado_401(escenario_entrega, caplog):
    with caplog.at_level(logging.WARNING, logger="seguridad"):
        respuesta = APIClient().get(
            f"/api/v1/entregas/{escenario_entrega.entrega.pk}"
        )

    assert respuesta.status_code == 401
    evento = [r for r in caplog.records if r.name == "seguridad"][0]
    assert evento.evento == "acceso_denegado"
    assert evento.status == 401


@pytest.mark.django_db
def test_acceso_a_recurso_ajeno_registra_acceso_denegado_403(
    escenario_entrega, caplog
):
    cliente = APIClient()
    cliente.credentials(
        HTTP_AUTHORIZATION=(
            "Bearer "
            + AuthService.generar_token(escenario_entrega.usuario_ajeno)
        )
    )

    with caplog.at_level(logging.WARNING, logger="seguridad"):
        respuesta = cliente.patch(
            f"/api/v1/entregas/{escenario_entrega.entrega.pk}",
            {"lugar": "Intruso"},
            format="json",
        )

    assert respuesta.status_code == 403
    evento = [r for r in caplog.records if r.name == "seguridad"][0]
    assert evento.evento == "acceso_denegado"
    assert evento.status == 403
    assert evento.usuario_id == escenario_entrega.usuario_ajeno.pk
    assert evento.ruta == f"/api/v1/entregas/{escenario_entrega.entrega.pk}"


@pytest.mark.django_db
def test_el_token_no_aparece_en_los_registros(escenario_entrega, caplog):
    token = AuthService.generar_token(escenario_entrega.usuario_ajeno)
    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    with caplog.at_level(logging.DEBUG):
        cliente.patch(
            f"/api/v1/entregas/{escenario_entrega.entrega.pk}",
            {"lugar": "Intruso"},
            format="json",
        )

    assert token not in caplog.text


# ------------------------------------------- limite de intentos (A07)

@pytest.mark.django_db
def test_el_inicio_de_sesion_se_limita_y_responde_429(
    usuario_con_clave, monkeypatch, caplog
):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "login", "3/min")
    cliente = APIClient()
    datos = {"correo": usuario_con_clave.correo, "contrasena": "mala-clave-1"}

    estados = [
        cliente.post("/api/v1/auth/login", datos, format="json").status_code
        for _ in range(3)
    ]
    with caplog.at_level(logging.WARNING, logger="seguridad"):
        limitada = cliente.post("/api/v1/auth/login", datos, format="json")

    assert estados == [401, 401, 401]
    assert limitada.status_code == 429
    assert limitada["Content-Type"] == "application/problem+json"
    assert "solicitudes_limitadas" in [
        getattr(r, "evento", None) for r in caplog.records
    ]


@pytest.mark.django_db
def test_el_limite_tambien_frena_al_que_acierta_la_clave_tras_muchos_intentos(
    usuario_con_clave, monkeypatch
):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "login", "2/min")
    cliente = APIClient()
    mala = {"correo": usuario_con_clave.correo, "contrasena": "mala-clave-1"}
    buena = {"correo": usuario_con_clave.correo, "contrasena": "Clave-correcta-1"}

    cliente.post("/api/v1/auth/login", mala, format="json")
    cliente.post("/api/v1/auth/login", mala, format="json")

    assert cliente.post("/api/v1/auth/login", buena, format="json").status_code == 429


@pytest.mark.django_db
def test_el_panel_limita_los_intentos_de_inicio_de_sesion(
    usuario_con_clave, settings
):
    settings.LOGIN_PANEL_MAX_INTENTOS = 2
    from django.test import Client

    cliente = Client()
    datos = {"correo": usuario_con_clave.correo, "contrasena": "mala-clave-1"}

    estados = [cliente.post("/panel/login/", datos).status_code for _ in range(3)]

    assert estados[:2] == [400, 400]
    assert estados[2] == 429