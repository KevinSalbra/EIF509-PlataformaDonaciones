"""
Autenticacion del modulo administrativo.

La API usa JWT (stateless); el modulo MVC usa sesion firmada en cookie.
El modelo Usuario no es el User de django.contrib.auth, por eso la
sesion guarda unicamente el id del usuario y en cada peticion se
vuelve a cargar y validar (activo + rol ADMINISTRADOR).
"""
from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from cr.ac.una.alimentaCR.data.models import Usuario

CLAVE_SESION = "panel_id_usuario"


def iniciar_sesion(request, usuario):
    # Nueva clave de sesion al autenticar: evita fijacion de sesion.
    request.session.cycle_key()
    request.session[CLAVE_SESION] = usuario.id_usuario


def cerrar_sesion(request):
    request.session.flush()


def usuario_de_sesion(request):
    id_usuario = request.session.get(CLAVE_SESION)
    if id_usuario is None:
        return None
    return Usuario.objects.filter(
        pk=id_usuario,
        estado=Usuario.Estado.ACTIVO,
        rol=Usuario.Rol.ADMINISTRADOR,
    ).first()


def requiere_administrador(vista):
    """Redirige al login si no hay un administrador activo en sesion."""

    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        usuario = usuario_de_sesion(request)
        if usuario is None:
            request.session.pop(CLAVE_SESION, None)
            destino = reverse("panel_login")
            return redirect(
                f"{destino}?{urlencode({'next': request.get_full_path()})}"
            )
        request.usuario_panel = usuario
        return vista(request, *args, **kwargs)

    return envoltura