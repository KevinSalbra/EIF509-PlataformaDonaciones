"""
Pruebas del modulo administrativo MVC (/panel/).

Cubren: autenticacion y autorizacion por rol, listado paginado,
formularios validados (errores por campo), patron Post/Redirect/Get
y proteccion CSRF, para dos casos de uso: Categorias y Organizaciones.

Datos de prueba: Usuario 1 = ADMINISTRADOR, Usuario 2 =
REPRESENTANTE_DONANTE (ver V2__insertar_datos_prueba.sql).
"""

import pytest
from django.test import Client

from cr.ac.una.alimentaCR.business.services import (
    CategoriaService,
    OrganizacionService,
    UsuarioService,
)
from cr.ac.una.alimentaCR.data.models import (
    Categoria,
    Organizacion,
    Usuario,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("preparar_esquema_flyway"),
]

CLAVE = "ClaveSegura#2026"


@pytest.fixture
def admin():
    return UsuarioService().crear(
        id_organizacion=1,
        nombre="Admin Panel",
        correo="admin.panel@alimentacr.test",
        contrasena=CLAVE,
        rol=Usuario.Rol.ADMINISTRADOR,
    )


@pytest.fixture
def donante():
    return UsuarioService().crear(
        id_organizacion=2,
        nombre="Donante Panel",
        correo="donante.panel@alimentacr.test",
        contrasena=CLAVE,
        rol=Usuario.Rol.REPRESENTANTE_DONANTE,
    )


@pytest.fixture
def cliente():
    # enforce_csrf_checks: el cliente de pruebas lo omite por defecto.
    return Client(enforce_csrf_checks=True)


def _token_csrf(cliente, url="/panel/login/"):
    cliente.get(url)
    return cliente.cookies["csrftoken"].value


def post(cliente, url, datos, **extra):
    datos = {**datos, "csrfmiddlewaretoken": _token_csrf(cliente)}
    return cliente.post(url, datos, **extra)


def entrar(cliente, usuario):
    respuesta = post(
        cliente,
        "/panel/login/",
        {"correo": usuario.correo, "contrasena": CLAVE},
    )
    assert respuesta.status_code == 302
    return respuesta


@pytest.fixture
def sesion_admin(cliente, admin):
    entrar(cliente, admin)
    return cliente


# ------------------------------------------------------------- acceso

def test_listado_sin_sesion_redirige_al_login(cliente):
    respuesta = cliente.get("/panel/categorias/")
    assert respuesta.status_code == 302
    assert respuesta["Location"].startswith("/panel/login/?next=")


def test_login_valido_redirige_al_listado(cliente, admin):
    respuesta = entrar(cliente, admin)
    assert respuesta["Location"] == "/panel/categorias/"
    assert cliente.get("/panel/categorias/").status_code == 200


def test_login_con_contrasena_incorrecta(cliente, admin):
    respuesta = post(
        cliente,
        "/panel/login/",
        {"correo": admin.correo, "contrasena": "otra"},
    )
    assert respuesta.status_code == 400
    assert "Credenciales inválidas." in respuesta.content.decode()


def test_login_rechaza_usuario_no_administrador(cliente, donante):
    respuesta = post(
        cliente,
        "/panel/login/",
        {"correo": donante.correo, "contrasena": CLAVE},
    )
    assert respuesta.status_code == 400
    assert cliente.get("/panel/categorias/").status_code == 302


def test_login_campos_vacios_muestran_errores(cliente):
    respuesta = post(cliente, "/panel/login/", {"correo": "", "contrasena": ""})
    assert respuesta.status_code == 400
    assert "Este campo es obligatorio." in respuesta.content.decode()


def test_login_ignora_next_externo(cliente, admin):
    respuesta = post(
        cliente,
        "/panel/login/",
        {
            "correo": admin.correo,
            "contrasena": CLAVE,
            "next": "https://sitio-malicioso.example/",
        },
    )
    assert respuesta["Location"] == "/panel/categorias/"


def test_logout_requiere_post_y_cierra_sesion(sesion_admin):
    assert sesion_admin.get("/panel/logout/").status_code == 405
    respuesta = post(sesion_admin, "/panel/logout/", {})
    assert respuesta.status_code == 302
    assert sesion_admin.get("/panel/categorias/").status_code == 302


def test_usuario_inactivado_pierde_el_acceso(sesion_admin, admin):
    Usuario.objects.filter(pk=admin.pk).update(
        estado=Usuario.Estado.INACTIVO
    )
    assert sesion_admin.get("/panel/categorias/").status_code == 302


# --------------------------------------------------------------- CSRF

def test_post_sin_token_csrf_es_rechazado(sesion_admin):
    respuesta = sesion_admin.post(
        "/panel/categorias/nueva/", {"nombre": "Sin token"}
    )
    assert respuesta.status_code == 403
    assert not Categoria.objects.filter(nombre="Sin token").exists()


def test_formulario_incluye_token_csrf(sesion_admin):
    html = sesion_admin.get("/panel/categorias/nueva/").content.decode()
    assert "csrfmiddlewaretoken" in html


# --------------------------------------------------------- categorias

def test_categorias_listado_paginado(sesion_admin):
    servicio = CategoriaService()
    for numero in range(12):
        servicio.crear(nombre=f"Categoria extra {numero:02d}")
    total = Categoria.objects.count()

    pagina1 = sesion_admin.get("/panel/categorias/")
    assert pagina1.status_code == 200
    assert len(pagina1.context["pagina"]) == 10
    assert pagina1.context["pagina"].paginator.count == total

    pagina2 = sesion_admin.get("/panel/categorias/?page=2")
    assert pagina2.context["pagina"].number == 2
    assert len(pagina2.context["pagina"]) == total - 10


def test_categorias_pagina_invalida_no_falla(sesion_admin):
    assert sesion_admin.get("/panel/categorias/?page=abc").status_code == 200
    assert sesion_admin.get("/panel/categorias/?page=999").status_code == 200


def test_categoria_crear_aplica_post_redirect_get(sesion_admin):
    respuesta = post(
        sesion_admin,
        "/panel/categorias/nueva/",
        {"nombre": "Productos congelados", "descripcion": "Congelados"},
    )
    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/panel/categorias/"

    categoria = Categoria.objects.get(nombre="Productos congelados")
    assert categoria.estado == Categoria.Estado.ACTIVA

    # El GET posterior al redireccionamiento muestra el mensaje.
    seguimiento = sesion_admin.get(respuesta["Location"])
    assert "Productos congelados" in seguimiento.content.decode()
    assert "creada" in seguimiento.content.decode()


def test_categoria_crear_nombre_vacio_muestra_error(sesion_admin):
    antes = Categoria.objects.count()
    respuesta = post(
        sesion_admin,
        "/panel/categorias/nueva/",
        {"nombre": "   ", "descripcion": ""},
    )
    assert respuesta.status_code == 400
    assert respuesta.context["form"].errors["nombre"]
    assert Categoria.objects.count() == antes


def test_categoria_crear_nombre_demasiado_largo(sesion_admin):
    respuesta = post(
        sesion_admin,
        "/panel/categorias/nueva/",
        {"nombre": "x" * 101, "descripcion": ""},
    )
    assert respuesta.status_code == 400
    assert "Máximo 100 caracteres." in respuesta.content.decode()


def test_categoria_crear_duplicada_error_de_negocio_en_el_campo(
    sesion_admin,
):
    existente = Categoria.objects.first()
    respuesta = post(
        sesion_admin,
        "/panel/categorias/nueva/",
        {"nombre": existente.nombre, "descripcion": ""},
    )
    assert respuesta.status_code == 400
    assert "Ya existe una categoria" in respuesta.content.decode()


def test_categoria_editar_actualiza_y_redirige(sesion_admin):
    categoria = CategoriaService().crear(nombre="Para editar")
    url = f"/panel/categorias/{categoria.id_categoria}/editar/"

    assert sesion_admin.get(url).status_code == 200

    respuesta = post(
        sesion_admin,
        url,
        {
            "nombre": "Editada",
            "descripcion": "Nueva descripcion",
            "estado": Categoria.Estado.INACTIVA,
        },
    )
    assert respuesta.status_code == 302

    categoria.refresh_from_db()
    assert categoria.nombre == "Editada"
    assert categoria.estado == Categoria.Estado.INACTIVA


def test_categoria_editar_estado_invalido(sesion_admin):
    categoria = CategoriaService().crear(nombre="Estado malo")
    respuesta = post(
        sesion_admin,
        f"/panel/categorias/{categoria.id_categoria}/editar/",
        {"nombre": "Estado malo", "descripcion": "", "estado": "XYZ"},
    )
    assert respuesta.status_code == 400
    assert respuesta.context["form"].errors["estado"]


def test_categoria_editar_inexistente_devuelve_404(sesion_admin):
    assert sesion_admin.get("/panel/categorias/999999/editar/").status_code == 404


# ------------------------------------------------------ organizaciones

def datos_organizacion(**cambios):
    datos = {
        "nombre": "Fundación Prueba",
        "tipo": Organizacion.Tipo.BENEFICIARIA,
        "cedula_juridica": "3-101-777001",
        "direccion": "Heredia, Costa Rica",
        "telefono": "2200-7001",
        "descripcion": "Organización de prueba.",
    }
    datos.update(cambios)
    return datos


def test_organizaciones_listado_paginado(sesion_admin):
    servicio = OrganizacionService()
    for numero in range(12):
        servicio.crear(
            nombre=f"Org extra {numero:02d}",
            tipo=Organizacion.Tipo.DONANTE,
            cedula_juridica=f"3-101-8000{numero:02d}",
            direccion="San José",
            telefono="2200-0000",
        )
    total = Organizacion.objects.count()

    pagina1 = sesion_admin.get("/panel/organizaciones/")
    assert pagina1.status_code == 200
    assert len(pagina1.context["pagina"]) == 10
    assert sesion_admin.get(
        "/panel/organizaciones/?page=2"
    ).context["pagina"].paginator.count == total


def test_organizacion_crear_valida_y_queda_pendiente(sesion_admin):
    respuesta = post(
        sesion_admin, "/panel/organizaciones/nueva/", datos_organizacion()
    )
    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/panel/organizaciones/"

    organizacion = Organizacion.objects.get(cedula_juridica="3-101-777001")
    assert organizacion.estado == Organizacion.Estado.PENDIENTE


def test_organizacion_crear_cedula_con_formato_invalido(sesion_admin):
    respuesta = post(
        sesion_admin,
        "/panel/organizaciones/nueva/",
        datos_organizacion(cedula_juridica="12345"),
    )
    assert respuesta.status_code == 400
    assert respuesta.context["form"].errors["cedula_juridica"]
    assert not Organizacion.objects.filter(nombre="Fundación Prueba").exists()


def test_organizacion_crear_telefono_invalido_y_tipo_invalido(sesion_admin):
    respuesta = post(
        sesion_admin,
        "/panel/organizaciones/nueva/",
        datos_organizacion(telefono="abc", tipo="OTRO"),
    )
    assert respuesta.status_code == 400
    errores = respuesta.context["form"].errors
    assert "telefono" in errores and "tipo" in errores


def test_organizacion_crear_cedula_duplicada(sesion_admin):
    existente = Organizacion.objects.first()
    respuesta = post(
        sesion_admin,
        "/panel/organizaciones/nueva/",
        datos_organizacion(cedula_juridica=existente.cedula_juridica),
    )
    assert respuesta.status_code == 400
    assert "Ya existe una organizacion" in respuesta.content.decode()


def test_organizacion_editar_actualiza_y_conserva_cedula(sesion_admin):
    organizacion = OrganizacionService().crear(
        nombre="Original",
        tipo=Organizacion.Tipo.DONANTE,
        cedula_juridica="3-101-777002",
        direccion="Alajuela",
        telefono="2200-7002",
    )
    url = f"/panel/organizaciones/{organizacion.id_organizacion}/editar/"
    assert sesion_admin.get(url).status_code == 200

    datos = datos_organizacion(
        nombre="Actualizada",
        tipo=Organizacion.Tipo.DONANTE,
        estado=Organizacion.Estado.APROBADA,
    )
    datos.pop("cedula_juridica")
    respuesta = post(sesion_admin, url, datos)
    assert respuesta.status_code == 302

    organizacion.refresh_from_db()
    assert organizacion.nombre == "Actualizada"
    assert organizacion.estado == Organizacion.Estado.APROBADA
    assert organizacion.cedula_juridica == "3-101-777002"


def test_organizacion_editar_inexistente_devuelve_404(sesion_admin):
    assert (
        sesion_admin.get("/panel/organizaciones/999999/editar/").status_code
        == 404
    )