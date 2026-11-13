"""
Bloqueo optimista : una actualizacion basada en una copia
desactualizada del registro se rechaza en lugar de pisar el cambio ajeno.

Operaciones con contencion real del dominio:
- Entrega: la coordinan a la vez la organizacion donante y la beneficiaria.
- Solicitud: el donante puede aceptarla mientras la beneficiaria la cancela.

Cada prueba crea sus propios datos (fixture `escenario_entrega`).
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.db import close_old_connections, connection

from cr.ac.una.alimentaCR.data.exceptions import ConflictoConcurrenciaError
from cr.ac.una.alimentaCR.data.models import Entrega, Solicitud
from cr.ac.una.alimentaCR.data.repositories import (
    EntregaRepository,
    SolicitudRepository,
)

pytestmark = pytest.mark.django_db


def test_una_entrega_nueva_inicia_en_la_version_cero(escenario_entrega):
    assert escenario_entrega.entrega.version == 0
    assert Entrega.objects.get(
        pk=escenario_entrega.entrega.pk
    ).version == 0


def test_cada_actualizacion_incrementa_la_version(escenario_entrega):
    repositorio = EntregaRepository()
    entrega = repositorio.obtener_por_id(escenario_entrega.entrega.pk)

    entrega.lugar = "Bodega 1"
    repositorio.guardar(entrega)
    assert entrega.version == 1

    entrega.lugar = "Bodega 2"
    repositorio.guardar(entrega)
    assert entrega.version == 2

    en_base = Entrega.objects.get(pk=entrega.pk)
    assert (en_base.version, en_base.lugar) == (2, "Bodega 2")


def test_segunda_actualizacion_simultanea_se_rechaza(escenario_entrega):
    """
    La prueba que pide el Laboratorio 7: dos operadores cargan la misma
    entrega (ambos con la version 0); el primero guarda y el segundo,
    que trabaja con una copia desactualizada, es rechazado.
    """
    repositorio = EntregaRepository()
    id_entrega = escenario_entrega.entrega.pk

    copia_a = repositorio.obtener_por_id(id_entrega)  # donante
    copia_b = repositorio.obtener_por_id(id_entrega)  # beneficiaria
    assert copia_a.version == copia_b.version == 0

    copia_a.lugar = "Bodega del donante"
    repositorio.guardar(copia_a)  # version 0 -> 1

    copia_b.lugar = "Bodega de la beneficiaria"  # aun tiene la version 0
    with pytest.raises(ConflictoConcurrenciaError):
        repositorio.guardar(copia_b)

    # No se perdio la actualizacion de la primera persona.
    en_base = Entrega.objects.get(pk=id_entrega)
    assert en_base.lugar == "Bodega del donante"
    assert en_base.version == 1


def test_tras_un_conflicto_se_puede_recargar_y_guardar(escenario_entrega):
    repositorio = EntregaRepository()
    id_entrega = escenario_entrega.entrega.pk

    copia_a = repositorio.obtener_por_id(id_entrega)
    copia_b = repositorio.obtener_por_id(id_entrega)
    copia_a.lugar = "A"
    repositorio.guardar(copia_a)

    copia_b.observaciones = "B"
    with pytest.raises(ConflictoConcurrenciaError):
        repositorio.guardar(copia_b)

    # El usuario recarga los datos y repite su cambio.
    recargada = repositorio.obtener_por_id(id_entrega)
    recargada.observaciones = "B"
    repositorio.guardar(recargada)

    en_base = Entrega.objects.get(pk=id_entrega)
    assert (en_base.lugar, en_base.observaciones) == ("A", "B")
    assert en_base.version == 2


def test_cancelar_con_copia_desactualizada_no_pisa_la_aceptacion(
    escenario_entrega,
):
    """Aceptar y cancelar la misma solicitud al mismo tiempo."""
    repositorio = SolicitudRepository()
    solicitud = escenario_entrega.solicitud
    # Parte de PENDIENTE para representar la carrera real.
    Solicitud.objects.filter(pk=solicitud.pk).update(
        estado=Solicitud.Estado.PENDIENTE
    )

    la_acepta_el_donante = repositorio.obtener_por_id(solicitud.pk)
    la_cancela_la_beneficiaria = repositorio.obtener_por_id(solicitud.pk)

    la_acepta_el_donante.estado = Solicitud.Estado.ACEPTADA
    repositorio.guardar(la_acepta_el_donante)

    la_cancela_la_beneficiaria.estado = Solicitud.Estado.CANCELADA
    with pytest.raises(ConflictoConcurrenciaError):
        repositorio.guardar(la_cancela_la_beneficiaria)

    assert Solicitud.objects.get(pk=solicitud.pk).estado == "ACEPTADA"


def test_un_conflicto_no_modifica_ninguna_columna(escenario_entrega):
    repositorio = EntregaRepository()
    id_entrega = escenario_entrega.entrega.pk
    desactualizada = repositorio.obtener_por_id(id_entrega)

    otra = repositorio.obtener_por_id(id_entrega)
    otra.lugar = "Lugar vigente"
    repositorio.guardar(otra)

    desactualizada.lugar = "Lugar obsoleto"
    desactualizada.confirmacion_donante = True
    with pytest.raises(ConflictoConcurrenciaError):
        repositorio.guardar(desactualizada)

    en_base = Entrega.objects.get(pk=id_entrega)
    assert en_base.lugar == "Lugar vigente"
    assert en_base.confirmacion_donante is False


@pytest.mark.django_db(transaction=True)
def test_dos_hilos_actualizan_a_la_vez_y_solo_uno_gana(escenario_entrega):
    """
    Dos conexiones reales (como dos peticiones simultaneas): ambas leen la
    entrega antes de que cualquiera escriba. Exactamente una guarda; la
    otra recibe el conflicto.
    """
    if connection.vendor != "postgresql":
        pytest.skip("Requiere conexiones concurrentes reales (PostgreSQL).")

    id_entrega = escenario_entrega.entrega.pk
    ambos_leyeron = Barrier(2, timeout=10)

    def actualizar(lugar):
        close_old_connections()
        try:
            repositorio = EntregaRepository()
            entrega = repositorio.obtener_por_id(id_entrega)
            ambos_leyeron.wait()  # los dos tienen la version 0
            entrega.lugar = lugar
            repositorio.guardar(entrega)
            return "guardada"
        except ConflictoConcurrenciaError:
            return "conflicto"
        finally:
            connection.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as ejecutor:
            resultados = sorted(
                futuro.result(timeout=20)
                for futuro in [
                    ejecutor.submit(actualizar, "Lugar A"),
                    ejecutor.submit(actualizar, "Lugar B"),
                ]
            )

        assert resultados == ["conflicto", "guardada"]
        en_base = Entrega.objects.get(pk=id_entrega)
        assert en_base.version == 1
        assert en_base.lugar in ("Lugar A", "Lugar B")
    finally:
        # transaction=True confirma los datos: se retiran para no afectar
        # a otras pruebas.
        e = escenario_entrega
        Entrega.objects.filter(pk=id_entrega).delete()
        Solicitud.objects.filter(pk=e.solicitud.pk).delete()
        for modelo in (e.donacion, e.categoria):
            modelo.delete()
        for modelo in (
            e.usuario_donante, e.usuario_beneficiario, e.usuario_ajeno,
            e.donante, e.beneficiaria, e.ajena,
        ):
            modelo.delete()