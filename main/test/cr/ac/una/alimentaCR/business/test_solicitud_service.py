from unittest.mock import Mock

import pytest

from cr.ac.una.alimentaCR.business.exceptions import (
    DonacionNoDisponibleError,
    SolicitudNoExisteError,
    SolicitudNoPendienteError,
    UsuarioNoAutorizadoError,
)
from cr.ac.una.alimentaCR.business.services import SolicitudService
from cr.ac.una.alimentaCR.data.models import (
    Donacion,
    Entrega,
    Solicitud,
    Usuario,
)


# ============================================================
# Datos auxiliares
# ============================================================

def crear_donacion_disponible():
    return Donacion(
        id_donacion=1,
        organizacion_donante_id=2,
        categoria_id=1,
        alimento="Arroz",
        cantidad="10.00",
        unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
        estado=Donacion.Estado.DISPONIBLE,
    )


def crear_solicitud(
    id_solicitud=1,
    donacion=None,
    estado=Solicitud.Estado.PENDIENTE,
):
    if donacion is None:
        donacion = crear_donacion_disponible()

    return Solicitud(
        id_solicitud=id_solicitud,
        donacion=donacion,
        organizacion_beneficiaria_id=4,
        estado=estado,
    )


def crear_usuario_autorizado():
    return Usuario(
        id_usuario=1,
        organizacion_id=2,
        nombre="Representante donante",
        correo="donante@prueba.com",
        contrasena="prueba",
        rol=Usuario.Rol.REPRESENTANTE_DONANTE,
        estado=Usuario.Estado.ACTIVO,
    )


def crear_servicio(
    solicitud=None,
    usuario=None,
    solicitudes_pendientes=None,
):
    solicitud_repository = Mock()
    donacion_repository = Mock()
    entrega_repository = Mock()
    usuario_repository = Mock()
    bitacora_repository = Mock()

    solicitud_repository.obtener_por_id.return_value = solicitud
    usuario_repository.obtener_por_id.return_value = usuario

    solicitud_repository.obtener_pendientes_por_donacion.return_value = (
        solicitudes_pendientes or []
    )

    def guardar_entrega(entrega):
        entrega.id_entrega = 100
        return entrega

    entrega_repository.guardar.side_effect = guardar_entrega

    servicio = SolicitudService(
        solicitud_repository=solicitud_repository,
        donacion_repository=donacion_repository,
        entrega_repository=entrega_repository,
        usuario_repository=usuario_repository,
        bitacora_repository=bitacora_repository,
    )

    return (
        servicio,
        solicitud_repository,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    )


def ejecutar_proceso_transaccional(
    servicio,
    id_solicitud,
    id_usuario,
):
    """
    Ejecuta la logica interna del metodo decorado con
    @transaction.atomic sin abrir una transaccion real.

    Esto permite mantener estas pruebas como unitarias,
    utilizando mocks y sin depender de PostgreSQL.

    El comportamiento real del rollback se prueba
    por separado mediante una prueba de integracion.
    """
    return (
        SolicitudService
        ._aceptar_solicitud_transaccional
        .__wrapped__(
            servicio,
            id_solicitud=id_solicitud,
            id_usuario=id_usuario,
        )
    )


# ============================================================
# 1. Caso exitoso
# ============================================================

def test_aceptar_solicitud_exitosamente():
    donacion = crear_donacion_disponible()

    solicitud = crear_solicitud(
        id_solicitud=1,
        donacion=donacion,
    )

    otra_solicitud = crear_solicitud(
        id_solicitud=2,
        donacion=donacion,
    )

    usuario = crear_usuario_autorizado()

    (
        servicio,
        solicitud_repository,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=solicitud,
        usuario=usuario,
        solicitudes_pendientes=[
            solicitud,
            otra_solicitud,
        ],
    )

    entrega = ejecutar_proceso_transaccional(
        servicio,
        id_solicitud=1,
        id_usuario=1,
    )

    # La bitacora se encuentra fuera de la transaccion
    # PostgreSQL, por lo que se prueba explicitamente.
    servicio._registrar_evento_bitacora(
        entrega,
        id_usuario=1,
    )

    assert solicitud.estado == Solicitud.Estado.ACEPTADA
    assert otra_solicitud.estado == Solicitud.Estado.RECHAZADA
    assert donacion.estado == Donacion.Estado.ASIGNADA

    assert entrega.id_entrega == 100
    assert entrega.solicitud == solicitud
    assert entrega.estado == Entrega.Estado.PENDIENTE
    assert entrega.confirmacion_donante is False
    assert entrega.confirmacion_beneficiario is False

    solicitud_repository.obtener_por_id.assert_called_once_with(1)
    usuario_repository.obtener_por_id.assert_called_once_with(1)

    solicitud_repository.obtener_pendientes_por_donacion.assert_called_once_with(
        1
    )

    donacion_repository.guardar.assert_called_once_with(
        donacion
    )

    entrega_repository.guardar.assert_called_once()

    bitacora_repository.registrar.assert_called_once()


# ============================================================
# 2. Solicitud inexistente
# ============================================================

def test_aceptar_solicitud_falla_si_no_existe():
    (
        servicio,
        solicitud_repository,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=None,
        usuario=crear_usuario_autorizado(),
    )

    with pytest.raises(SolicitudNoExisteError):
        ejecutar_proceso_transaccional(
            servicio,
            id_solicitud=999,
            id_usuario=1,
        )

    solicitud_repository.obtener_por_id.assert_called_once_with(
        999
    )

    usuario_repository.obtener_por_id.assert_not_called()
    donacion_repository.guardar.assert_not_called()
    entrega_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 3. Solicitud no pendiente
# ============================================================

def test_aceptar_solicitud_falla_si_no_esta_pendiente():
    solicitud = crear_solicitud(
        estado=Solicitud.Estado.ACEPTADA,
    )

    (
        servicio,
        _,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=solicitud,
        usuario=crear_usuario_autorizado(),
    )

    with pytest.raises(SolicitudNoPendienteError):
        ejecutar_proceso_transaccional(
            servicio,
            id_solicitud=1,
            id_usuario=1,
        )

    usuario_repository.obtener_por_id.assert_not_called()
    donacion_repository.guardar.assert_not_called()
    entrega_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 4. Usuario no autorizado
# ============================================================

def test_aceptar_solicitud_falla_si_usuario_no_es_propietario():
    donacion = crear_donacion_disponible()

    solicitud = crear_solicitud(
        donacion=donacion,
    )

    usuario = crear_usuario_autorizado()

    # La donacion pertenece a la organizacion 2,
    # pero el usuario pertenece a otra organizacion.
    usuario.organizacion_id = 999

    (
        servicio,
        _,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=solicitud,
        usuario=usuario,
    )

    with pytest.raises(UsuarioNoAutorizadoError):
        ejecutar_proceso_transaccional(
            servicio,
            id_solicitud=1,
            id_usuario=1,
        )

    usuario_repository.obtener_por_id.assert_called_once_with(
        1
    )

    donacion_repository.guardar.assert_not_called()
    entrega_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 5. Usuario inexistente
# ============================================================

def test_aceptar_solicitud_falla_si_usuario_no_existe():
    donacion = crear_donacion_disponible()

    solicitud = crear_solicitud(
        donacion=donacion,
    )

    (
        servicio,
        _,
        donacion_repository,
        entrega_repository,
        usuario_repository,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=solicitud,
        usuario=None,
    )

    with pytest.raises(UsuarioNoAutorizadoError):
        ejecutar_proceso_transaccional(
            servicio,
            id_solicitud=1,
            id_usuario=999,
        )

    usuario_repository.obtener_por_id.assert_called_once_with(
        999
    )

    donacion_repository.guardar.assert_not_called()
    entrega_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()


# ============================================================
# 6. Donacion no disponible
# ============================================================

def test_aceptar_solicitud_falla_si_donacion_no_disponible():
    donacion = crear_donacion_disponible()
    donacion.estado = Donacion.Estado.ASIGNADA

    solicitud = crear_solicitud(
        donacion=donacion,
    )

    (
        servicio,
        solicitud_repository,
        donacion_repository,
        entrega_repository,
        _,
        bitacora_repository,
    ) = crear_servicio(
        solicitud=solicitud,
        usuario=crear_usuario_autorizado(),
    )

    with pytest.raises(DonacionNoDisponibleError):
        ejecutar_proceso_transaccional(
            servicio,
            id_solicitud=1,
            id_usuario=1,
        )

    solicitud_repository.obtener_pendientes_por_donacion.assert_not_called()
    donacion_repository.guardar.assert_not_called()
    entrega_repository.guardar.assert_not_called()
    bitacora_repository.registrar.assert_not_called()