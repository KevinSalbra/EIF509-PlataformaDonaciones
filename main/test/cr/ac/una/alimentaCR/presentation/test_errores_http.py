"""
Pruebas de los manejadores 404 y 500 (fuera de DRF).

Una ruta inexistente de la API responde con Problem Details; fuera de
/api/ se conserva la respuesta HTML de Django. Ninguna filtra trazas.
No necesitan base de datos.
"""

import json

from django.test import Client, RequestFactory
from django.urls import get_resolver

from cr.ac.una.alimentaCR.presentation import exception_handler as eh

TIPO_PROBLEMA = "application/problem+json"


def test_ruta_inexistente_de_la_api_devuelve_problem_details():
    respuesta = Client().get("/api/v1/no-existe")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    cuerpo = respuesta.json()
    assert cuerpo["status"] == 404
    assert cuerpo["title"] == "Not Found"
    assert cuerpo["instance"] == "/api/v1/no-existe"
    assert "Traceback" not in respuesta.content.decode()


def test_ruta_inexistente_fuera_de_la_api_conserva_el_html_de_django():
    respuesta = Client().get("/ruta-que-no-existe/")

    assert respuesta.status_code == 404
    assert respuesta["Content-Type"].startswith("text/html")


def test_error_500_en_la_api_devuelve_problem_details():
    peticion = RequestFactory().get("/api/v1/donaciones")

    respuesta = eh.manejador_500(peticion)

    assert respuesta.status_code == 500
    assert respuesta["Content-Type"].startswith(TIPO_PROBLEMA)
    cuerpo = json.loads(respuesta.content)
    assert cuerpo["status"] == 500
    assert cuerpo["instance"] == "/api/v1/donaciones"


def test_error_500_fuera_de_la_api_conserva_el_html_de_django():
    peticion = RequestFactory().get("/panel/categorias/")

    respuesta = eh.manejador_500(peticion)

    assert respuesta.status_code == 500
    assert respuesta["Content-Type"].startswith("text/html")


def test_los_manejadores_estan_registrados_en_las_urls():
    resolvedor = get_resolver()

    assert resolvedor.resolve_error_handler(404) is eh.manejador_404
    assert resolvedor.resolve_error_handler(500) is eh.manejador_500