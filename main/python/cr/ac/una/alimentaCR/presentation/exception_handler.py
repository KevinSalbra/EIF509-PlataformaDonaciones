import logging
from http import HTTPStatus

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from cr.ac.una.alimentaCR.business import exceptions as err

logger = logging.getLogger(__name__)

TIPO_PROBLEMA = "application/problem+json"

# Excepcion de negocio -> codigo HTTP. El orden importa: ErrorNegocio
# (la clase base) va al final como respaldo.
MAPA_EXCEPCIONES = {
    err.SolicitudNoExisteError: status.HTTP_404_NOT_FOUND,
    err.OrganizacionNoExisteError: status.HTTP_404_NOT_FOUND,
    err.CategoriaNoExisteError: status.HTTP_404_NOT_FOUND,
    err.UsuarioNoExisteError: status.HTTP_404_NOT_FOUND,
    err.SolicitudNoPendienteError: status.HTTP_409_CONFLICT,
    err.DonacionNoDisponibleError: status.HTTP_409_CONFLICT,
    err.CorreoDuplicadoError: status.HTTP_409_CONFLICT,
    err.UsuarioNoAutorizadoError: status.HTTP_403_FORBIDDEN,
    err.OrganizacionNoAutorizadaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    err.CategoriaInactivaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    err.CantidadInvalidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    err.FechaLimiteInvalidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    err.RolOrganizacionIncompatibleError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    err.ErrorNegocio: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def _problema(codigo, detalle, request, respuesta=None, **extra):
    """Arma un cuerpo Problem Details (RFC 9457)."""
    cuerpo = {
        "type": "about:blank",
        "title": HTTPStatus(codigo).phrase,
        "status": codigo,
        "detail": detalle,
        "instance": request.path,
    }
    cuerpo.update(extra)
    if respuesta is None:
        respuesta = Response(status=codigo)
    respuesta.data = cuerpo
    respuesta.content_type = TIPO_PROBLEMA
    return respuesta


def manejador_global(exc, context):
    request = context["request"]

    # 1. Errores de formato (serializers / @Valid)
    if isinstance(exc, ValidationError):
        return _problema(
            status.HTTP_400_BAD_REQUEST,
            "La solicitud contiene datos invalidos.",
            request,
            errores=exc.detail,
        )

    # 2. Excepciones de negocio
    for tipo, codigo in MAPA_EXCEPCIONES.items():
        if isinstance(exc, tipo):
            return _problema(codigo, str(exc), request)

    # 3. Excepciones propias de DRF/Django (404, 401, 403, 405, ...)
    respuesta = exception_handler(exc, context)
    if respuesta is not None:
        detalle = ""
        if isinstance(respuesta.data, dict):
            detalle = str(respuesta.data.get("detail", ""))
        return _problema(respuesta.status_code, detalle, request, respuesta)

    # 4. Cualquier otro error: se registra en el log
    logger.exception("Error no controlado en %s", request.path)
    return _problema(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Ocurrio un error interno. Intente nuevamente mas tarde.",
        request,
    )