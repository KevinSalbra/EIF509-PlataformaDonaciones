import pytest

from django.db import connection
from django.test.utils import CaptureQueriesContext

from cr.ac.una.alimentaCR.data.models import Donacion


@pytest.mark.django_db
def test_n_mas_uno_sin_optimizacion():
    """
    Demuestra el problema N+1.

    Se obtiene la lista de donaciones con una consulta inicial.
    Luego, al acceder a organizacion_donante y categoria para
    cada donacion, Django ejecuta consultas adicionales.
    """

    with CaptureQueriesContext(connection) as consultas:
        donaciones = Donacion.objects.all()

        resultados = []

        for donacion in donaciones:
            resultados.append(
                (
                    donacion.alimento,
                    donacion.organizacion_donante.nombre,
                    donacion.categoria.nombre,
                )
            )

    cantidad_consultas = len(consultas)

    print(
        "\nCantidad de consultas sin optimizacion:",
        cantidad_consultas
    )

    for indice, consulta in enumerate(
        consultas.captured_queries,
        start=1
    ):
        print(f"\nConsulta {indice}:")
        print(consulta["sql"])

    assert len(resultados) > 0

    # Debe existir más de una consulta debido al N+1.
    assert cantidad_consultas > 1


@pytest.mark.django_db
def test_n_mas_uno_con_select_related():
    """
    Corrige el problema N+1 mediante select_related.

    Django realiza un JOIN con organizacion y categoria,
    obteniendo toda la información necesaria en una sola
    consulta SQL.
    """

    with CaptureQueriesContext(connection) as consultas:
        donaciones = Donacion.objects.select_related(
            "organizacion_donante",
            "categoria"
        )

        resultados = []

        for donacion in donaciones:
            resultados.append(
                (
                    donacion.alimento,
                    donacion.organizacion_donante.nombre,
                    donacion.categoria.nombre,
                )
            )

    cantidad_consultas = len(consultas)

    print(
        "\nCantidad de consultas con optimizacion:",
        cantidad_consultas
    )

    for indice, consulta in enumerate(
        consultas.captured_queries,
        start=1
    ):
        print(f"\nConsulta {indice}:")
        print(consulta["sql"])

    assert len(resultados) > 0

    # select_related debe resolver las relaciones FK
    # en una sola consulta SQL.
    assert cantidad_consultas == 1