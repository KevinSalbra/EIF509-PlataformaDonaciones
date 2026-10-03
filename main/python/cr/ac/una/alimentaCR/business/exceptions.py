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

class OrganizacionNoExisteError(ErrorNegocio):
    """No existe una Organizacion con el id indicado."""


class OrganizacionNoAutorizadaError(ErrorNegocio):
    """La Organizacion no es donante o no se encuentra aprobada."""


class CategoriaNoExisteError(ErrorNegocio):
    """No existe una Categoria con el id indicado."""


class CategoriaInactivaError(ErrorNegocio):
    """La Categoria seleccionada no se encuentra activa."""


class CantidadInvalidaError(ErrorNegocio):
    """La cantidad de alimento debe ser mayor que cero."""


class FechaLimiteInvalidaError(ErrorNegocio):
    """La fecha limite de retiro debe ser posterior a la fecha actual."""



class UsuarioNoExisteError(ErrorNegocio):
    """No existe un Usuario con el id indicado."""


class CorreoDuplicadoError(ErrorNegocio):
    """Ya existe un Usuario registrado con ese correo."""


class RolOrganizacionIncompatibleError(ErrorNegocio):
    """El rol del Usuario no corresponde al tipo de su Organizacion."""



class DonacionNoExisteError(ErrorNegocio):
    """No existe una Donacion con el id indicado."""


class SolicitudDuplicadaError(ErrorNegocio):
    """La organizacion ya tiene una Solicitud pendiente para esa Donacion."""



class EntregaNoExisteError(ErrorNegocio):
    """No existe una Entrega con el id indicado."""


class EntregaNoPendienteError(ErrorNegocio):
    """La Entrega ya no esta pendiente y no admite cambios."""


class FechaAcordadaInvalidaError(ErrorNegocio):
    """La fecha acordada de la Entrega es anterior a la fecha actual."""