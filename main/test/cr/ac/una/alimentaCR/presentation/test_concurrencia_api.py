"""
Concurrencia en la API (Laboratorio 7): la donante y la beneficiaria
coordinan la misma entrega al mismo tiempo (PATCH /api/v1/entregas/{id}).

El cliente puede enviar la `version` que leyo; si otra persona modifico la
entrega, la API responde 409 (Problem Details) y no pisa el cambio ajeno.
"""
import logging

import pytest
from rest_framework.test import APIClient

from cr.ac.una.alimentaCR.business.services import AuthService
from cr.ac.una.alimentaCR.data.models import Entrega

pytestmark = pytest.mark.django_db

TIPO_PROBLEMA = "application/problem+json"


def cliente_de(usuario):
    cliente = APIClient()
    cliente.credentials(
        HTTP_AUTHORIZATION=f"Bearer {AuthService.generar_token(usuario)}"
    )
    return cliente


def url(entrega):
    return f"/api/v1/entregas/{entrega.pk}"


def test_la_entrega_expone_su_version(escenario_entrega):
    cliente = cliente_de(escenario_entrega.usuario_donante)

    respuesta = cliente.get(url(escenario_entrega.entrega))

    assert respuesta.status_code == 200
    assert respuesta.json()["version"] == 0


def test_coordinar_con_la_version_vigente_200_e_incrementa_la_version(
    escenario_entrega,
):
    cliente = cliente_de(escenario_entrega.usuario_donante)

    respuesta = cliente.patch(
        url(escenario_entrega.entrega),
        {"lugar": "Bodega central", "version": 0},
        format="json",
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["lugar"] == "Bodega central"
    assert cuerpo["version"] == 1


def test_coordinar_con_version_obsoleta_409_con_problem_details(
    escenario_entrega,
):
    cliente = cliente_de(escenario_entrega.usuario_beneficiario)
    Entrega.objects.filter(pk=escenario_entrega.entrega.pk).update(
        version=3, lugar="Lugar vigente"
    )

    respuesta = cliente.patch(
        url(escenario_entrega.entrega),
        {"lugar": "Lugar obsoleto", "version": 0},
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta["Content-Type"] == TIPO_PROBLEMA
    cuerpo = respuesta.json()
    assert cuerpo["status"] == 409
    assert cuerpo["title"] == "Conflict"
    assert "modificada por otra persona" in cuerpo["detail"]
    # No se filtran trazas ni detalles internos.
    assert "Traceback" not in respuesta.content.decode()

    en_base = Entrega.objects.get(pk=escenario_entrega.entrega.pk)
    assert en_base.lugar == "Lugar vigente"
    assert en_base.version == 3


def test_dos_operadores_el_segundo_recibe_409_y_puede_reintentar(
    escenario_entrega,
):
    """
    Escenario completo: ambas organizaciones consultan la entrega (version
    0). La donante coordina primero; la beneficiaria, con datos ya
    obsoletos, recibe 409, recarga y repite su cambio con exito.
    """
    donante = cliente_de(escenario_entrega.usuario_donante)
    beneficiaria = cliente_de(escenario_entrega.usuario_beneficiario)
    ruta = url(escenario_entrega.entrega)

    version_donante = donante.get(ruta).json()["version"]
    version_beneficiaria = beneficiaria.get(ruta).json()["version"]
    assert version_donante == version_beneficiaria == 0

    primera = donante.patch(
        ruta,
        {"lugar": "Bodega del donante", "version": version_donante},
        format="json",
    )
    assert primera.status_code == 200

    segunda = beneficiaria.patch(
        ruta,
        {"observaciones": "Llegamos a las 3", "version": version_beneficiaria},
        format="json",
    )
    assert segunda.status_code == 409

    # Recarga, ve el cambio del donante y repite el suyo.
    vigente = beneficiaria.get(ruta).json()
    assert vigente["lugar"] == "Bodega del donante"
    reintento = beneficiaria.patch(
        ruta,
        {"observaciones": "Llegamos a las 3", "version": vigente["version"]},
        format="json",
    )
    assert reintento.status_code == 200
    assert reintento.json()["lugar"] == "Bodega del donante"
    assert reintento.json()["observaciones"] == "Llegamos a las 3"
    assert reintento.json()["version"] == 2


def test_coordinar_sin_enviar_version_sigue_funcionando(escenario_entrega):
    cliente = cliente_de(escenario_entrega.usuario_donante)

    respuesta = cliente.patch(
        url(escenario_entrega.entrega),
        {"lugar": "Bodega central"},
        format="json",
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["version"] == 1


def test_enviar_solo_la_version_sin_cambios_es_400(escenario_entrega):
    cliente = cliente_de(escenario_entrega.usuario_donante)

    respuesta = cliente.patch(
        url(escenario_entrega.entrega), {"version": 0}, format="json"
    )

    assert respuesta.status_code == 400


def test_un_conflicto_queda_registrado_como_evento_de_seguridad(
    escenario_entrega, caplog
):
    cliente = cliente_de(escenario_entrega.usuario_donante)
    Entrega.objects.filter(pk=escenario_entrega.entrega.pk).update(version=5)

    with caplog.at_level(logging.WARNING, logger="seguridad"):
        cliente.patch(
            url(escenario_entrega.entrega),
            {"lugar": "X", "version": 0},
            format="json",
        )

    eventos = [r for r in caplog.records if r.name == "seguridad"]
    assert [e.evento for e in eventos] == ["conflicto_concurrencia"]
    assert eventos[0].usuario_id == escenario_entrega.usuario_donante.pk