from abc import ABC, abstractmethod

from ...data.models import Solicitud
from ..exceptions import SolicitudNoPendienteError


class EstadoSolicitud(ABC):
    """
    Patron State para el ciclo de vida de una Solicitud.

    Senal que justifica el patron: que transiciones son validas
    (aceptar, rechazar, cancelar) depende exclusivamente del estado
    actual de la Solicitud. Sin este patron, cada servicio que
    manipule una Solicitud -- aceptar_solicitud en la Meta 1,
    cancelar_solicitud en el Proceso 4 mas adelante -- terminaria
    repitiendo el mismo bloque de "if estado != PENDIENTE: raise ...".
    Centralizar la regla aqui evita esa duplicacion y hace explicitas,
    en un solo lugar, las transiciones permitidas del dominio.
    """

    nombre: str

    @abstractmethod
    def aceptar(self, solicitud: Solicitud) -> None:
        ...

    @abstractmethod
    def rechazar(self, solicitud: Solicitud) -> None:
        ...

    @abstractmethod
    def cancelar(self, solicitud: Solicitud) -> None:
        ...

    def _transicion_invalida(self, solicitud: Solicitud) -> SolicitudNoPendienteError:
        return SolicitudNoPendienteError(
            f"La solicitud {solicitud.id_solicitud} no esta pendiente "
            f"(estado actual: {self.nombre})."
        )


class PendienteState(EstadoSolicitud):
    nombre = Solicitud.Estado.PENDIENTE

    def aceptar(self, solicitud: Solicitud) -> None:
        solicitud.estado = Solicitud.Estado.ACEPTADA

    def rechazar(self, solicitud: Solicitud) -> None:
        solicitud.estado = Solicitud.Estado.RECHAZADA

    def cancelar(self, solicitud: Solicitud) -> None:
        solicitud.estado = Solicitud.Estado.CANCELADA


class _EstadoFinal(EstadoSolicitud):
    """
    Estado terminal comun a ACEPTADA, RECHAZADA y CANCELADA: ninguna
    de estas tres transiciones vuelve a ser valida una vez alcanzado
    un estado final.
    """

    def aceptar(self, solicitud: Solicitud) -> None:
        raise self._transicion_invalida(solicitud)

    def rechazar(self, solicitud: Solicitud) -> None:
        raise self._transicion_invalida(solicitud)

    def cancelar(self, solicitud: Solicitud) -> None:
        raise self._transicion_invalida(solicitud)


class AceptadaState(_EstadoFinal):
    nombre = Solicitud.Estado.ACEPTADA


class RechazadaState(_EstadoFinal):
    nombre = Solicitud.Estado.RECHAZADA


class CanceladaState(_EstadoFinal):
    nombre = Solicitud.Estado.CANCELADA


_ESTADOS = {
    Solicitud.Estado.PENDIENTE: PendienteState(),
    Solicitud.Estado.ACEPTADA: AceptadaState(),
    Solicitud.Estado.RECHAZADA: RechazadaState(),
    Solicitud.Estado.CANCELADA: CanceladaState(),
}


def obtener_estado(valor_estado: str) -> EstadoSolicitud:
    """Devuelve el objeto State correspondiente al valor de
    Solicitud.estado guardado en la base de datos."""
    return _ESTADOS[valor_estado]