import pytest

from cr.ac.una.alimentaCR.data.models import Donacion
from cr.ac.una.alimentaCR.data.repositories.donacion_repository import (
    DonacionRepository,
)


@pytest.mark.django_db
def test_obtener_donaciones_disponibles():
    """
    Verifica que DonacionRepository obtenga únicamente
    las donaciones cuyo estado es DISPONIBLE.

    La prueba se ejecuta contra PostgreSQL real levantado
    mediante Testcontainers y preparado con Flyway.
    """

    repository = DonacionRepository()

    donaciones = repository.obtener_disponibles()

    resultados = list(donaciones)

    assert len(resultados) > 0

    assert all(
        donacion.estado == Donacion.Estado.DISPONIBLE
        for donacion in resultados
    )

@pytest.mark.django_db
def test_obtener_donaciones_disponibles_por_categoria():
    """
    Verifica que el repositorio retorne únicamente
    donaciones disponibles de la categoría indicada.
    """

    repository = DonacionRepository()

    categoria_id = 4

    donaciones = list(
        repository.obtener_disponibles_por_categoria(
            categoria_id
        )
    )

    assert len(donaciones) > 0

    assert all(
        donacion.estado == Donacion.Estado.DISPONIBLE
        for donacion in donaciones
    )

    assert all(
        donacion.categoria_id == categoria_id
        for donacion in donaciones
    )

@pytest.mark.django_db
def test_filtrar_donaciones_por_estado_y_organizacion():
    """
    Verifica que el repositorio pueda combinar filtros
    dinámicos de estado y organización donante.
    """

    repository = DonacionRepository()

    organizacion_id = 2

    donaciones = list(
        repository.filtrar_donaciones(
            estado=Donacion.Estado.DISPONIBLE,
            organizacion_id=organizacion_id
        )
    )

    assert len(donaciones) > 0

    assert all(
        donacion.estado == Donacion.Estado.DISPONIBLE
        for donacion in donaciones
    )

    assert all(
        donacion.organizacion_donante_id == organizacion_id
        for donacion in donaciones
    )

@pytest.mark.django_db
def test_obtener_donacion_por_id_desde_base_repository():
    """
    Verifica que DonacionRepository utilice correctamente
    el método genérico obtener_por_id heredado de BaseRepository.
    """

    repository = DonacionRepository()

    donacion = repository.obtener_por_id(1)

    assert donacion is not None
    assert donacion.pk == 1
    assert donacion.alimento == "Manzanas"