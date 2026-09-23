from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock

import pytest
from django.utils import timezone

from cr.ac.una.alimentaCR.business.exceptions import (
    CantidadInvalidaError,
    CategoriaInactivaError,
    CategoriaNoExisteError,
    FechaLimiteInvalidaError,
    OrganizacionNoAutorizadaError,
    OrganizacionNoExisteError,
)
from cr.ac.una.alimentaCR.business.services import DonacionService
from cr.ac.una.alimentaCR.data.models import (
    Categoria,
    Donacion,
    Organizacion,
)


# ============================================================
# Datos auxiliares
# ============================================================

def crear_organizacion_valida():
    return Organizacion(
        id_organizacion=2,
        nombre="Supermercado La Esperanza",
        tipo=Organizacion.Tipo.DONANTE,
        cedula_juridica="3-101-999999",
        descripcion="Organizacion de prueba",
        direccion="Costa Rica",
        telefono="2222-2222",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )


def crear_categoria_valida():
    return Categoria(
        id_categoria=1,
        nombre="Frutas y verduras",
        descripcion="Categoria de prueba",
        estado=Categoria.Estado.ACTIVA,
    )


def crear_servicio(
    organizacion=None,
    categoria=None,
):
    organizacion_repository = Mock()
    categoria_repository = Mock()
    donacion_repository = Mock()
    bitacora_repository = Mock()

    organizacion_repository.obtener_por_id.return_value = organizacion
    categoria_repository.obtener_por_id.return_value = categoria

    # Simula el guardado sin utilizar PostgreSQL.
    def guardar_donacion(donacion):
        donacion.id_donacion = 100
        return donacion

    donacion_repository.guardar.side_effect = guardar_donacion

    servicio = DonacionService(
        organizacion_repository=organizacion_repository,
        categoria_repository=categoria_repository,
        donacion_repository=donacion_repository,
        bitacora_repository=bitacora_repository,
    )

    return (
        servicio,
        organizacion_repository,
        categoria_repository,
        donacion_repository,
        bitacora_repository,
    )


# ============================================================
# 1. Caso exitoso
# ============================================================

def test_publicar_donacion_exitosamente():
    organizacion = crear_organizacion_valida()
    categoria = crear_categoria_valida()

    (
        servicio,
        organizacion_repository,
        categoria_repository,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=organizacion,
        categoria=categoria,
    )

    fecha_limite = timezone.localdate() + timedelta(days=7)

    resultado = servicio.publicar_donacion(
        id_organizacion=2,
        id_categoria=1,
        alimento="Peras",
        descripcion="Donacion de prueba",
        cantidad=Decimal("12.50"),
        unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
        fecha_limite_retiro=fecha_limite,
    )

    assert resultado.id_donacion == 100
    assert resultado.alimento == "Peras"
    assert resultado.cantidad == Decimal("12.50")
    assert resultado.estado == Donacion.Estado.DISPONIBLE
    assert resultado.organizacion_donante == organizacion
    assert resultado.categoria == categoria

    organizacion_repository.obtener_por_id.assert_called_once_with(2)
    categoria_repository.obtener_por_id.assert_called_once_with(1)

    donacion_repository.guardar.assert_called_once()
    bitacora_repository.registrar.assert_called_once()


# ============================================================
# 2. Organizacion inexistente
# ============================================================

def test_publicar_donacion_falla_si_organizacion_no_existe():
    (
        servicio,
        _,
        categoria_repository,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=None,
        categoria=crear_categoria_valida(),
    )

    with pytest.raises(OrganizacionNoExisteError):
        servicio.publicar_donacion(
            id_organizacion=999,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    categoria_repository.obtener_por_id.assert_not_called()
    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 3. Organizacion no autorizada
# ============================================================

def test_publicar_donacion_falla_si_organizacion_no_es_donante():
    organizacion = crear_organizacion_valida()
    organizacion.tipo = Organizacion.Tipo.BENEFICIARIA

    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=organizacion,
        categoria=crear_categoria_valida(),
    )

    with pytest.raises(OrganizacionNoAutorizadaError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 4. Organizacion no aprobada
# ============================================================

def test_publicar_donacion_falla_si_organizacion_no_esta_aprobada():
    organizacion = crear_organizacion_valida()
    organizacion.estado = Organizacion.Estado.PENDIENTE

    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=organizacion,
        categoria=crear_categoria_valida(),
    )

    with pytest.raises(OrganizacionNoAutorizadaError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 5. Categoria inexistente
# ============================================================

def test_publicar_donacion_falla_si_categoria_no_existe():
    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=crear_organizacion_valida(),
        categoria=None,
    )

    with pytest.raises(CategoriaNoExisteError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=999,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 6. Categoria inactiva
# ============================================================

def test_publicar_donacion_falla_si_categoria_esta_inactiva():
    categoria = crear_categoria_valida()
    categoria.estado = Categoria.Estado.INACTIVA

    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=crear_organizacion_valida(),
        categoria=categoria,
    )

    with pytest.raises(CategoriaInactivaError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 7. Cantidad invalida
# ============================================================

def test_publicar_donacion_falla_si_cantidad_es_cero():
    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=crear_organizacion_valida(),
        categoria=crear_categoria_valida(),
    )

    with pytest.raises(CantidadInvalidaError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("0.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=(
                timezone.localdate() + timedelta(days=7)
            ),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 8. Fecha limite invalida
# ============================================================

def test_publicar_donacion_falla_si_fecha_limite_no_es_futura():
    (
        servicio,
        _,
        _,
        donacion_repository,
        bitacora_repository,
    ) = crear_servicio(
        organizacion=crear_organizacion_valida(),
        categoria=crear_categoria_valida(),
    )

    with pytest.raises(FechaLimiteInvalidaError):
        servicio.publicar_donacion(
            id_organizacion=2,
            id_categoria=1,
            alimento="Peras",
            descripcion="Prueba",
            cantidad=Decimal("10.00"),
            unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
            fecha_limite_retiro=timezone.localdate(),
        )

    donacion_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()