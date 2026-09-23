from abc import ABC, abstractmethod

from django.utils import timezone

from ...data.models import Categoria, Organizacion
from ..exceptions import (
    CantidadInvalidaError,
    CategoriaInactivaError,
    FechaLimiteInvalidaError,
    OrganizacionNoAutorizadaError,
)


class EspecificacionPublicacion(ABC):
    """
    Specification base para las reglas que determinan si una
    Donacion puede ser publicada.
    """

    @abstractmethod
    def validar(self) -> None:
        pass


class OrganizacionPuedeDonarSpecification(EspecificacionPublicacion):
    """
    Verifica que la organizacion sea donante y se encuentre aprobada.
    """

    def __init__(self, organizacion: Organizacion):
        self.organizacion = organizacion

    def validar(self) -> None:
        if (
            self.organizacion.tipo != Organizacion.Tipo.DONANTE
            or self.organizacion.estado != Organizacion.Estado.APROBADA
        ):
            raise OrganizacionNoAutorizadaError(
                f"La organizacion "
                f"{self.organizacion.id_organizacion} "
                f"no esta autorizada para publicar donaciones."
            )


class CategoriaActivaSpecification(EspecificacionPublicacion):
    """
    Verifica que la categoria seleccionada se encuentre activa.
    """

    def __init__(self, categoria: Categoria):
        self.categoria = categoria

    def validar(self) -> None:
        if self.categoria.estado != Categoria.Estado.ACTIVA:
            raise CategoriaInactivaError(
                f"La categoria {self.categoria.id_categoria} "
                f"no se encuentra activa."
            )


class CantidadPositivaSpecification(EspecificacionPublicacion):
    """
    Verifica que la cantidad de alimento sea mayor que cero.
    """

    def __init__(self, cantidad):
        self.cantidad = cantidad

    def validar(self) -> None:
        if self.cantidad <= 0:
            raise CantidadInvalidaError(
                "La cantidad debe ser mayor que cero."
            )


class FechaLimiteFuturaSpecification(EspecificacionPublicacion):
    """
    Verifica que la fecha limite de retiro sea posterior a hoy.
    """

    def __init__(self, fecha_limite_retiro):
        self.fecha_limite_retiro = fecha_limite_retiro

    def validar(self) -> None:
        if self.fecha_limite_retiro <= timezone.localdate():
            raise FechaLimiteInvalidaError(
                "La fecha limite de retiro debe ser posterior "
                "a la fecha actual."
            )