"""
Registro de eventos de seguridad (OWASP A09).

Cada evento se escribe como una linea JSON en el logger "seguridad" con un
campo `evento` estable para poder filtrarlo. No se registran contrasenas ni
tokens; para el inicio de sesion fallido se registra el correo intentado y la
IP, que es lo que permite detectar fuerza bruta.
"""
import logging

logger = logging.getLogger("seguridad")


def ip_cliente(request):
    """IP del cliente. Detras del proxy de Render llega en X-Forwarded-For."""
    reenviada = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if reenviada:
        return reenviada.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _usuario(request):
    usuario = getattr(request, "user", None)
    return getattr(usuario, "id_usuario", None)


def login_fallido(request, correo, origen="api"):
    logger.warning(
        "Inicio de sesion fallido",
        extra={
            "evento": "login_fallido",
            "origen": origen,
            "correo": correo,
            "ip": ip_cliente(request),
        },
    )


def acceso_denegado(request, codigo):
    logger.warning(
        "Acceso denegado (%s) a %s %s",
        codigo, request.method, request.path,
        extra={
            "evento": "acceso_denegado",
            "status": codigo,
            "usuario_id": _usuario(request),
            "metodo": request.method,
            "ruta": request.path,
            "ip": ip_cliente(request),
        },
    )


def conflicto_concurrencia(request, detalle):
    logger.warning(
        "Conflicto de concurrencia en %s %s",
        request.method, request.path,
        extra={
            "evento": "conflicto_concurrencia",
            "usuario_id": _usuario(request),
            "metodo": request.method,
            "ruta": request.path,
            "detalle": detalle,
        },
    )


def solicitudes_limitadas(request):
    logger.warning(
        "Demasiadas solicitudes a %s",
        request.path,
        extra={
            "evento": "solicitudes_limitadas",
            "ruta": request.path,
            "ip": ip_cliente(request),
        },
    )