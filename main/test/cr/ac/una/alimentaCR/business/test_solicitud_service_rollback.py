from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.utils import timezone

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
    SolicitudRepository,
    UsuarioRepository,
)


class EntregaRepositoryConFallo:
    """
    Doble de prueba que simula un fallo al momento de
    persistir la Entrega.

    El fallo ocurre despues de que el servicio ya intento
    modificar las Solicitudes y la Donacion, permitiendo
    comprobar que transaction.atomic realiza el rollback.
    """

    def guardar(self, entrega):
        raise RuntimeError(
            "Fallo simulado al crear la entrega."
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("preparar_esquema_flyway")
def test_rollback_si_falla_creacion_entrega():
    # ========================================================
    # 1. Preparar datos
    # ========================================================

    organizacion_donante = Organizacion.objects.create(
        nombre="Donante prueba rollback",
        tipo=Organizacion.Tipo.DONANTE,
        cedula_juridica="ROLLBACK-DONANTE-001",
        descripcion="Organizacion creada para prueba de rollback",
        direccion="Costa Rica",
        telefono="2222-1111",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    organizacion_beneficiaria_1 = Organizacion.objects.create(
        nombre="Beneficiaria rollback 1",
        tipo=Organizacion.Tipo.BENEFICIARIA,
        cedula_juridica="ROLLBACK-BEN-001",
        descripcion="Beneficiaria de prueba",
        direccion="Costa Rica",
        telefono="2222-2222",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    organizacion_beneficiaria_2 = Organizacion.objects.create(
        nombre="Beneficiaria rollback 2",
        tipo=Organizacion.Tipo.BENEFICIARIA,
        cedula_juridica="ROLLBACK-BEN-002",
        descripcion="Beneficiaria de prueba",
        direccion="Costa Rica",
        telefono="2222-3333",
        estado=Organizacion.Estado.APROBADA,
        fecha_registro=timezone.now(),
    )

    categoria = Categoria.objects.create(
        nombre="Categoria rollback",
        descripcion="Categoria para prueba de rollback",
        estado=Categoria.Estado.ACTIVA,
    )

    donacion = Donacion.objects.create(
        organizacion_donante=organizacion_donante,
        categoria=categoria,
        alimento="Arroz rollback",
        descripcion="Donacion para comprobar rollback",
        cantidad="20.00",
        unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
        fecha_publicacion=timezone.now(),
        fecha_limite_retiro=(
            timezone.localdate() + timedelta(days=10)
        ),
        estado=Donacion.Estado.DISPONIBLE,
    )

    solicitud_aceptada = Solicitud.objects.create(
        donacion=donacion,
        organizacion_beneficiaria=organizacion_beneficiaria_1,
        fecha_solicitud=timezone.now(),
        estado=Solicitud.Estado.PENDIENTE,
        observacion="Solicitud principal",
    )

    otra_solicitud = Solicitud.objects.create(
        donacion=donacion,
        organizacion_beneficiaria=organizacion_beneficiaria_2,
        fecha_solicitud=timezone.now(),
        estado=Solicitud.Estado.PENDIENTE,
        observacion="Solicitud que deberia rechazarse",
    )

    usuario = Usuario.objects.create(
        organizacion=organizacion_donante,
        nombre="Usuario rollback",
        correo="rollback@alimenta.test",
        contrasena="contrasena-prueba",
        telefono="8888-8888",
        rol=Usuario.Rol.REPRESENTANTE_DONANTE,
        estado=Usuario.Estado.ACTIVO,
        fecha_registro=timezone.now(),
    )

    # ========================================================
    # 2. Crear servicio
    # ========================================================

    bitacora_repository = Mock()

    servicio = SolicitudService(
        solicitud_repository=SolicitudRepository(),
        donacion_repository=DonacionRepository(),
        entrega_repository=EntregaRepositoryConFallo(),
        usuario_repository=UsuarioRepository(),
        bitacora_repository=bitacora_repository,
    )

    # ========================================================
    # 3. Ejecutar el proceso y provocar el fallo
    # ========================================================

    with pytest.raises(
        RuntimeError,
        match="Fallo simulado al crear la entrega",
    ):
        servicio.aceptar_solicitud(
            id_solicitud=solicitud_aceptada.id_solicitud,
            id_usuario=usuario.id_usuario,
        )

    # ========================================================
    # 4. Recargar desde PostgreSQL
    # ========================================================

    solicitud_aceptada.refresh_from_db()
    otra_solicitud.refresh_from_db()
    donacion.refresh_from_db()

    # ========================================================
    # 5. Comprobar rollback
    # ========================================================

    assert (
        solicitud_aceptada.estado
        == Solicitud.Estado.PENDIENTE
    )

    assert (
        otra_solicitud.estado
        == Solicitud.Estado.PENDIENTE
    )

    assert (
        donacion.estado
        == Donacion.Estado.DISPONIBLE
    )

    assert not Entrega.objects.filter(
        solicitud_id=solicitud_aceptada.id_solicitud
    ).exists()

    # La bitacora esta fuera de la transaccion y nunca debe
    # ejecutarse si falla la parte relacional.
    bitacora_repository.registrar.assert_not_called()