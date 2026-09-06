import pytest

from cr.ac.una.alimentaCR.data.models import Solicitud
from cr.ac.una.alimentaCR.data.repositories.solicitud_repository import (
    SolicitudRepository,
)


@pytest.mark.django_db
def test_obtener_solicitudes_pendientes_por_donacion():
    """
    Verifica que el repositorio retorne únicamente
    solicitudes pendientes asociadas a una donación específica.
    """

    repository = SolicitudRepository()

    donacion_id = 1

    solicitudes = list(
        repository.obtener_pendientes_por_donacion(
            donacion_id
        )
    )

    assert len(solicitudes) > 0

    assert all(
        solicitud.estado == Solicitud.Estado.PENDIENTE
        for solicitud in solicitudes
    )

    assert all(
        solicitud.donacion_id == donacion_id
        for solicitud in solicitudes
    )

@pytest.mark.django_db
def test_filtrar_solicitudes_por_estado_y_donacion():
    """
    Verifica que el repositorio pueda combinar filtros
    dinámicos de estado y donación.
    """

    repository = SolicitudRepository()

    donacion_id = 1

    solicitudes = list(
        repository.filtrar_solicitudes(
            estado=Solicitud.Estado.PENDIENTE,
            donacion_id=donacion_id
        )
    )

    assert len(solicitudes) > 0

    assert all(
        solicitud.estado == Solicitud.Estado.PENDIENTE
        for solicitud in solicitudes
    )

    assert all(
        solicitud.donacion_id == donacion_id
        for solicitud in solicitudes
    )