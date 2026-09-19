class ErrorNegocio(RuntimeError):
    """
    Excepcion base para los errores de reglas de negocio de AlimentaCR.

    Extiende RuntimeError (equivalente en Python a extender
    RuntimeException en Java, tal como lo pide el enunciado del
    Laboratorio 4) para que sea una excepcion no verificada: no es
    obligatorio declararla ni capturarla explicitamente en cada
    llamada, pero sigue siendo especifica del dominio.
    """


class SolicitudNoExisteError(ErrorNegocio):
    """No existe una Solicitud con el id indicado."""


class SolicitudNoPendienteError(ErrorNegocio):
    """La Solicitud no esta en estado PENDIENTE y por lo tanto no
    puede ser aceptada ni rechazada."""


class DonacionNoDisponibleError(ErrorNegocio):
    """La Donacion asociada a la Solicitud ya no esta en estado
    DISPONIBLE (fue asignada, entregada, cancelada o vencida)."""


class UsuarioNoAutorizadoError(ErrorNegocio):
    """El Usuario que intenta aceptar la Solicitud no pertenece a la
    Organizacion donante de la Donacion (no es el propietario)."""