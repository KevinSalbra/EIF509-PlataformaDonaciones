import subprocess

import pytest
from django.db import connections


@pytest.fixture(scope="session", autouse=True)
def preparar_esquema_flyway(django_db_setup, django_db_blocker):
    """
    Prepara con Flyway el esquema relacional de la base temporal
    creada por pytest-django.

    Flujo:
    1. pytest-django crea la base temporal.
    2. Se verifica que sea una base de pruebas.
    3. Se limpia el esquema public creado por Django.
    4. Flyway ejecuta V1, V2, etc. desde cero.
    5. Se ejecutan los tests.
    6. pytest-django elimina la base temporal.
    """

    conexion = connections["default"]
    nombre_base_pruebas = conexion.settings_dict["NAME"]

    print(
        f"\nPreparando base de datos de pruebas: "
        f"{nombre_base_pruebas}"
    )

    # Protección para no tocar accidentalmente
    # la base normal de desarrollo.
    if not nombre_base_pruebas.startswith("test_"):
        raise RuntimeError(
            "La base de datos no parece ser una base temporal "
            f"de pytest: {nombre_base_pruebas}"
        )

    print(
        f"Limpiando esquema public de "
        f"{nombre_base_pruebas}"
    )

    # pytest-django ya creó la base, pero también puede haber
    # creado objetos en public. Los eliminamos para que Flyway
    # sea el único responsable de crear el esquema relacional.
    with django_db_blocker.unblock():
        with conexion.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")

    flyway_url = (
        "jdbc:postgresql://postgres:5432/"
        f"{nombre_base_pruebas}"
    )

    print(
        f"Ejecutando Flyway sobre: "
        f"{nombre_base_pruebas}"
    )

    subprocess.run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "-e",
            f"FLYWAY_URL={flyway_url}",
            "flyway",
            "migrate",
        ],
        check=True,
    )

    print(
        f"Esquema Flyway preparado correctamente en "
        f"{nombre_base_pruebas}\n"
    )