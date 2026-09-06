import os
import subprocess

import pytest
from django.conf import settings
from django.db import connections

from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_testcontainer():
    """
    Levanta una instancia temporal de PostgreSQL mediante
    Testcontainers y configura Django para utilizarla.
    """

    print("\nIniciando PostgreSQL con Testcontainers...")

    with PostgresContainer(
        "postgres:18.6-alpine",
        driver=None
    ) as postgres:

        host = postgres.get_container_host_ip()
        puerto = postgres.get_exposed_port(5432)

        usuario = postgres.username
        contrasena = postgres.password
        nombre_base = postgres.dbname

        print(
            f"PostgreSQL temporal disponible en "
            f"{host}:{puerto}"
        )

        configuracion = settings.DATABASES["default"]

        configuracion["HOST"] = host
        configuracion["PORT"] = puerto
        configuracion["USER"] = usuario
        configuracion["PASSWORD"] = contrasena
        configuracion["NAME"] = nombre_base

        connections["default"].close()

        yield postgres

    print("\nPostgreSQL temporal eliminado.")


@pytest.fixture(scope="session", autouse=True)
def preparar_esquema_flyway(
    postgres_testcontainer,
    django_db_setup,
    django_db_blocker
):
    """
    Ejecuta Flyway sobre la base temporal creada
    por pytest-django dentro del PostgreSQL de Testcontainers.
    """

    conexion = connections["default"]

    nombre_base_pruebas = conexion.settings_dict["NAME"]

    puerto = postgres_testcontainer.get_exposed_port(5432)

    usuario = postgres_testcontainer.username
    contrasena = postgres_testcontainer.password

    print(
        f"\nPreparando esquema con Flyway en "
        f"{nombre_base_pruebas}"
    )

    if not nombre_base_pruebas.startswith("test_"):
        raise RuntimeError(
            "La base de datos no parece ser una base "
            f"temporal de pytest: {nombre_base_pruebas}"
        )

    # Limpiamos el esquema creado por Django.
    with django_db_blocker.unblock():
        with conexion.cursor() as cursor:
            cursor.execute(
                "DROP SCHEMA public CASCADE;"
            )
            cursor.execute(
                "CREATE SCHEMA public;"
            )

    ruta_migraciones = os.path.abspath(
        "database/migrations"
    )

    flyway_url = (
        "jdbc:postgresql://host.docker.internal:"
        f"{puerto}/{nombre_base_pruebas}"
    )

    print(
        f"Ejecutando Flyway sobre: "
        f"{nombre_base_pruebas}"
    )

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--add-host",
            "host.docker.internal:host-gateway",
            "-v",
            f"{ruta_migraciones}:/flyway/sql",
            "flyway/flyway:13.3.0",
            f"-url={flyway_url}",
            f"-user={usuario}",
            f"-password={contrasena}",
            "migrate",
        ],
        check=True,
    )

    print(
        f"Esquema Flyway preparado correctamente en "
        f"{nombre_base_pruebas}\n"
    )