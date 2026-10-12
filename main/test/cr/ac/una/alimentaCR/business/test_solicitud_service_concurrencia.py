
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from unittest.mock import Mock

import pytest
from django.db import close_old_connections, connection, transaction
from django.utils import timezone

from cr.ac.una.alimentaCR.business.exceptions import (
    DonacionNoDisponibleError,
    SolicitudNoPendienteError,
)
from cr.ac.una.alimentaCR.business.services import SolicitudService
from cr.ac.una.alimentaCR.data.models import (
    Categoria,
    Donacion,
    Entrega,
    Organizacion,
    Solicitud,
    Usuario,
)
from cr.ac.una.alimentaCR.data.repositories import (
    DonacionRepository,
    EntregaRepository,
    SolicitudRepository,
    UsuarioRepository,
)


class DonacionRepositoryConPausa(DonacionRepository):
    """
    Permite mantener bloqueada la donacion durante
    la primera transaccion para comprobar la espera
    de la segunda transaccion.
    """

    def __init__(self, bloqueo_obtenido, liberar_bloqueo):
        self.bloqueo_obtenido = bloqueo_obtenido
        self.liberar_bloqueo = liberar_bloqueo

    def obtener_por_id_para_actualizar(self, id_donacion):
        donacion = super().obtener_por_id_para_actualizar(id_donacion)

        self.bloqueo_obtenido.set()

        if not self.liberar_bloqueo.wait(timeout=10):
            raise TimeoutError(
                "No se libero el bloqueo de la primera transaccion."
            )

        return donacion


def ejecutar_aceptacion(id_solicitud, id_usuario, repositorio):
    """
    Cada hilo utiliza su propia conexion a PostgreSQL.
    La bitacora se simula para no depender de MongoDB.
    """
    close_old_connections()

    try:
        servicio = SolicitudService(
            solicitud_repository=SolicitudRepository(),
            donacion_repository=repositorio,
            entrega_repository=EntregaRepository(),
            usuario_repository=UsuarioRepository(),
            bitacora_repository=Mock(),
        )

        return servicio.aceptar_solicitud(
            id_solicitud=id_solicitud,
            id_usuario=id_usuario,
        )
    finally:
        connection.close()


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("preparar_esquema_flyway")
def test_dos_solicitudes_no_pueden_aceptarse_simultaneamente():
    assert connection.vendor == "postgresql"

    # ========================================================
    # 1. Preparar datos
    # ========================================================

    donante = Organizacion.objects.create(
        nombre="Donante concurrencia",
        tipo=Organizacion.Tipo.DONANTE,
        cedula_juridica="CONC-DON-001",
        descripcion="Prueba de concurrencia",
        direccion="Costa Rica",
        telefono="2222-1111",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    beneficiaria_1 = Organizacion.objects.create(
        nombre="Beneficiaria concurrencia 1",
        tipo=Organizacion.Tipo.BENEFICIARIA,
        cedula_juridica="CONC-BEN-001",
        descripcion="Beneficiaria de prueba",
        direccion="Costa Rica",
        telefono="2222-2222",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    beneficiaria_2 = Organizacion.objects.create(
        nombre="Beneficiaria concurrencia 2",
        tipo=Organizacion.Tipo.BENEFICIARIA,
        cedula_juridica="CONC-BEN-002",
        descripcion="Beneficiaria de prueba",
        direccion="Costa Rica",
        telefono="2222-3333",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    categoria = Categoria.objects.create(
        nombre="Categoria concurrencia",
        descripcion="Prueba de bloqueo",
        estado=Categoria.Estado.ACTIVA,
    )

    donacion = Donacion.objects.create(
        organizacion_donante=donante,
        categoria=categoria,
        alimento="Arroz concurrencia",
        descripcion="Donacion de prueba",
        cantidad="20.00",
        unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
        fecha_publicacion=timezone.now(),
        fecha_limite_retiro=timezone.localdate() + timedelta(days=10),
        estado=Donacion.Estado.DISPONIBLE,
    )

    solicitud_1 = Solicitud.objects.create(
        donacion=donacion,
        organizacion_beneficiaria=beneficiaria_1,
        fecha_solicitud=timezone.now(),
        estado=Solicitud.Estado.PENDIENTE,
        observacion="Primera solicitud",
    )

    solicitud_2 = Solicitud.objects.create(
        donacion=donacion,
        organizacion_beneficiaria=beneficiaria_2,
        fecha_solicitud=timezone.now(),
        estado=Solicitud.Estado.PENDIENTE,
        observacion="Segunda solicitud",
    )

    usuario = Usuario.objects.create(
        organizacion=donante,
        nombre="Usuario concurrencia",
        correo="concurrencia@alimenta.test",
        contrasena="contrasena-prueba",
        telefono="8888-8888",
        rol=Usuario.Rol.REPRESENTANTE_DONANTE,
        estado=Usuario.Estado.ACTIVO,
        fecha_registro=timezone.now(),
    )

    # ========================================================
    # 2. Preparar los dos procesos concurrentes
    # ========================================================

    bloqueo_obtenido = Event()
    liberar_bloqueo = Event()

    repositorio_1 = DonacionRepositoryConPausa(
        bloqueo_obtenido,
        liberar_bloqueo,
    )

    repositorio_2 = DonacionRepository()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futuro_1 = executor.submit(
            ejecutar_aceptacion,
            solicitud_1.id_solicitud,
            usuario.id_usuario,
            repositorio_1,
        )

        try:
            # Esperar hasta que la primera transaccion
            # tenga bloqueada la donacion.
            assert bloqueo_obtenido.wait(timeout=10)

            futuro_2 = executor.submit(
                ejecutar_aceptacion,
                solicitud_2.id_solicitud,
                usuario.id_usuario,
                repositorio_2,
            )

            # Mientras la primera transaccion conserva
            # el bloqueo, la segunda no debe terminar.
            assert not futuro_2.done()

        finally:
            # Liberar la primera transaccion.
            liberar_bloqueo.set()

        entrega = futuro_1.result(timeout=15)

        with pytest.raises(
            (DonacionNoDisponibleError, SolicitudNoPendienteError)
        ):
            futuro_2.result(timeout=15)

    # ========================================================
    # 3. Comprobar el estado final en PostgreSQL
    # ========================================================

    donacion.refresh_from_db()
    solicitud_1.refresh_from_db()
    solicitud_2.refresh_from_db()

    assert donacion.estado == Donacion.Estado.ASIGNADA
    assert solicitud_1.estado == Solicitud.Estado.ACEPTADA
    assert solicitud_2.estado == Solicitud.Estado.RECHAZADA

    assert Entrega.objects.filter(
        solicitud__donacion=donacion
    ).count() == 1

    assert entrega.solicitud_id == solicitud_1.id_solicitud
