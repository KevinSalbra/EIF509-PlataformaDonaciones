import os
import subprocess
import uuid
from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone
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


@pytest.fixture(scope="session")
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


@pytest.fixture(autouse=True)
def limpiar_cache():
    """
    Los contadores del limite de intentos de inicio de sesion viven en la
    cache (LocMem). Se limpian para que una prueba no afecte a otra.
    """
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def escenario_entrega(db, preparar_esquema_flyway):
    """
    Crea, con datos propios (no depende de los de Flyway), una donacion
    asignada con su solicitud ACEPTADA y su entrega PENDIENTE, mas los
    representantes de ambas organizaciones.
    """
    from cr.ac.una.alimentaCR.data.models import (
        Categoria,
        Donacion,
        Entrega,
        Organizacion,
        Solicitud,
        Usuario,
    )

    sufijo = uuid.uuid4().hex[:8]
    ahora = timezone.now()

    def organizacion(tipo, nombre):
        return Organizacion.objects.create(
            nombre=f"{nombre} {sufijo}",
            tipo=tipo,
            cedula_juridica=f"E-{nombre[:3].upper()}-{sufijo}",
            descripcion="Datos de prueba",
            direccion="Costa Rica",
            telefono="2222-0000",
            estado=Organizacion.Estado.APROBADA,
            fecha_registro=ahora,
        )

    def usuario(org, rol, nombre):
        return Usuario.objects.create(
            organizacion=org,
            nombre=f"{nombre} {sufijo}",
            correo=f"{nombre.lower()}.{sufijo}@alimenta.test",
            contrasena="hash-de-prueba",
            telefono="8888-0000",
            rol=rol,
            estado=Usuario.Estado.ACTIVO,
            fecha_registro=ahora,
        )

    donante = organizacion(Organizacion.Tipo.DONANTE, "Donante")
    beneficiaria = organizacion(Organizacion.Tipo.BENEFICIARIA, "Beneficiaria")
    ajena = organizacion(Organizacion.Tipo.BENEFICIARIA, "Ajena")

    categoria = Categoria.objects.create(
        nombre=f"Categoria {sufijo}",
        descripcion="Datos de prueba",
        estado=Categoria.Estado.ACTIVA,
    )
    donacion = Donacion.objects.create(
        organizacion_donante=donante,
        categoria=categoria,
        alimento=f"Arroz {sufijo}",
        descripcion="Datos de prueba",
        cantidad="20.00",
        unidad_medida=Donacion.UnidadMedida.KILOGRAMO,
        fecha_publicacion=ahora,
        fecha_limite_retiro=timezone.localdate() + timedelta(days=10),
        estado=Donacion.Estado.ASIGNADA,
    )
    solicitud = Solicitud.objects.create(
        donacion=donacion,
        organizacion_beneficiaria=beneficiaria,
        fecha_solicitud=ahora,
        estado=Solicitud.Estado.ACEPTADA,
        observacion="Datos de prueba",
    )
    entrega = Entrega.objects.create(
        solicitud=solicitud,
        fecha_creacion=ahora,
        confirmacion_donante=False,
        confirmacion_beneficiario=False,
        estado=Entrega.Estado.PENDIENTE,
    )

    return SimpleNamespace(
        donante=donante,
        beneficiaria=beneficiaria,
        ajena=ajena,
        categoria=categoria,
        donacion=donacion,
        solicitud=solicitud,
        entrega=entrega,
        usuario_donante=usuario(
            donante, Usuario.Rol.REPRESENTANTE_DONANTE, "Donante"
        ),
        usuario_beneficiario=usuario(
            beneficiaria, Usuario.Rol.REPRESENTANTE_BENEFICIARIA, "Benef"
        ),
        usuario_ajeno=usuario(
            ajena, Usuario.Rol.REPRESENTANTE_BENEFICIARIA, "Ajeno"
        ),
    )