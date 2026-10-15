"""
Vistas del modulo administrativo (patron MVC).

Cada formulario sigue Post/Redirect/Get: un POST valido guarda y
responde con 302 hacia el listado (o la pagina de origen); un POST
invalido vuelve a mostrar el formulario con sus errores. La proteccion
CSRF la aplica CsrfViewMiddleware y cada plantilla incluye
{% csrf_token %}.
"""
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from cr.ac.una.alimentaCR.business.exceptions import (
    CategoriaNoExisteError,
    CedulaJuridicaDuplicadaError,
    NombreCategoriaDuplicadoError,
    OrganizacionNoExisteError,
)
from cr.ac.una.alimentaCR.data.models import Usuario
from cr.ac.una.alimentaCR.business.services import (
    CategoriaService,
    OrganizacionService,
    UsuarioService,
)

from .autenticacion import (
    cerrar_sesion,
    iniciar_sesion,
    requiere_administrador,
    usuario_de_sesion,
)
from .forms import CategoriaForm, LoginForm, OrganizacionForm

TAMANO_PAGINA = 10


def _paginar(request, coleccion):
    """Pagina la coleccion con ?page=N; un valor invalido va a la 1."""
    paginador = Paginator(coleccion, TAMANO_PAGINA)
    try:
        return paginador.page(request.GET.get("page"))
    except PageNotAnInteger:
        return paginador.page(1)
    except EmptyPage:
        return paginador.page(paginador.num_pages)


def _destino_seguro(request, valor, por_defecto):
    if valor and url_has_allowed_host_and_scheme(
        valor,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return valor
    return por_defecto


# ---------------------------------------------------------------- sesion

@require_http_methods(["GET", "POST"])
def login(request):
    if usuario_de_sesion(request) is not None:
        return redirect("panel_categorias")

    siguiente = request.POST.get("next") or request.GET.get("next", "")
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        usuario = UsuarioService().autenticar(
            correo=form.cleaned_data["correo"],
            contrasena=form.cleaned_data["contrasena"],
        )
        if usuario is None or usuario.rol != Usuario.Rol.ADMINISTRADOR:
            # Mismo mensaje para ambos casos: no revela si el correo existe.
            form.add_error(None, "Credenciales inválidas.")
        else:
            iniciar_sesion(request, usuario)
            return redirect(
                _destino_seguro(request, siguiente, "/panel/categorias/")
            )

    return render(
        request,
        "panel/login.html",
        {"form": form, "next": siguiente},
        status=400 if form.errors else 200,
    )


@require_POST
def logout(request):
    cerrar_sesion(request)
    return redirect("panel_login")


def inicio(request):
    return redirect("panel_categorias")


# ------------------------------------------------------------ categorias

@requiere_administrador
def categoria_lista(request):
    pagina = _paginar(request, CategoriaService().listar(orden=["nombre"]))
    return render(
        request,
        "panel/categoria_lista.html",
        {"pagina": pagina, "seccion": "categorias"},
    )


@requiere_administrador
@require_http_methods(["GET", "POST"])
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            categoria = CategoriaService().crear(
                nombre=form.cleaned_data["nombre"],
                descripcion=form.cleaned_data["descripcion"],
            )
        except NombreCategoriaDuplicadoError as error:
            form.add_error("nombre", str(error))
        else:
            messages.success(
                request, f"Categoría '{categoria.nombre}' creada."
            )
            return redirect("panel_categorias")

    return render(
        request,
        "panel/categoria_form.html",
        {"form": form, "titulo": "Nueva categoría", "seccion": "categorias"},
        status=400 if form.errors else 200,
    )


@requiere_administrador
@require_http_methods(["GET", "POST"])
def categoria_editar(request, id_categoria):
    servicio = CategoriaService()
    try:
        categoria = servicio.obtener(id_categoria)
    except CategoriaNoExisteError:
        raise Http404("La categoría no existe.")

    inicial = {
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion or "",
        "estado": categoria.estado,
    }
    form = CategoriaForm(
        request.POST or None, initial=inicial, con_estado=True
    )

    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        try:
            servicio.actualizar(
                id_categoria=id_categoria,
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                estado=datos["estado"],
            )
        except NombreCategoriaDuplicadoError as error:
            form.add_error("nombre", str(error))
        else:
            messages.success(request, "Categoría actualizada.")
            return redirect("panel_categorias")

    return render(
        request,
        "panel/categoria_form.html",
        {
            "form": form,
            "titulo": f"Editar categoría #{id_categoria}",
            "seccion": "categorias",
        },
        status=400 if form.errors else 200,
    )


# ---------------------------------------------------------- organizaciones

@requiere_administrador
def organizacion_lista(request):
    pagina = _paginar(request, OrganizacionService().listar(orden=["nombre"]))
    return render(
        request,
        "panel/organizacion_lista.html",
        {"pagina": pagina, "seccion": "organizaciones"},
    )


@requiere_administrador
@require_http_methods(["GET", "POST"])
def organizacion_crear(request):
    form = OrganizacionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        try:
            organizacion = OrganizacionService().crear(
                nombre=datos["nombre"],
                tipo=datos["tipo"],
                cedula_juridica=datos["cedula_juridica"],
                direccion=datos["direccion"],
                telefono=datos["telefono"],
                descripcion=datos["descripcion"],
            )
        except CedulaJuridicaDuplicadaError as error:
            form.add_error("cedula_juridica", str(error))
        else:
            messages.success(
                request, f"Organización '{organizacion.nombre}' registrada."
            )
            return redirect("panel_organizaciones")

    return render(
        request,
        "panel/organizacion_form.html",
        {
            "form": form,
            "titulo": "Nueva organización",
            "seccion": "organizaciones",
        },
        status=400 if form.errors else 200,
    )


@requiere_administrador
@require_http_methods(["GET", "POST"])
def organizacion_editar(request, id_organizacion):
    servicio = OrganizacionService()
    try:
        organizacion = servicio.obtener(id_organizacion)
    except OrganizacionNoExisteError:
        raise Http404("La organización no existe.")

    inicial = {
        "nombre": organizacion.nombre,
        "tipo": organizacion.tipo,
        "direccion": organizacion.direccion,
        "telefono": organizacion.telefono,
        "descripcion": organizacion.descripcion or "",
        "estado": organizacion.estado,
    }
    form = OrganizacionForm(
        request.POST or None, initial=inicial, edicion=True
    )

    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        servicio.actualizar(
            id_organizacion=id_organizacion,
            nombre=datos["nombre"],
            tipo=datos["tipo"],
            direccion=datos["direccion"],
            telefono=datos["telefono"],
            estado=datos["estado"],
            descripcion=datos["descripcion"],
        )
        messages.success(request, "Organización actualizada.")
        return redirect("panel_organizaciones")

    return render(
        request,
        "panel/organizacion_form.html",
        {
            "form": form,
            "titulo": f"Editar organización #{id_organizacion}",
            "organizacion": organizacion,
            "seccion": "organizaciones",
        },
        status=400 if form.errors else 200,
    )