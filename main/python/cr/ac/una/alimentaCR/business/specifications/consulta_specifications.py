from abc import ABC, abstractmethod
from datetime import timedelta
from functools import reduce

from django.db.models import Q
from django.utils import timezone

from ...data.models import Donacion


class ConsultaSpecification(ABC):
    """
    Specification de consulta: encapsula un criterio de filtrado de
    una coleccion como un objeto reutilizable y combinable.

    Se pueden componer con & (y) y | (o):

        (DonacionPorEstadoSpecification("DISPONIBLE")
         & DonacionPorCategoriaSpecification(3)).aplicar(queryset)
    """

    @abstractmethod
    def a_q(self) -> Q:
        """Devuelve la condicion como un objeto Q de Django."""

    def __and__(self, otra: "ConsultaSpecification") -> "ConsultaSpecification":
        return AndSpecification(self, otra)

    def __or__(self, otra: "ConsultaSpecification") -> "ConsultaSpecification":
        return OrSpecification(self, otra)

    def aplicar(self, queryset):
        return queryset.filter(self.a_q())


class AndSpecification(ConsultaSpecification):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def a_q(self) -> Q:
        return self.izquierda.a_q() & self.derecha.a_q()


class OrSpecification(ConsultaSpecification):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def a_q(self) -> Q:
        return self.izquierda.a_q() | self.derecha.a_q()


class TodoSpecification(ConsultaSpecification):
    """Elemento neutro: no filtra nada."""

    def a_q(self) -> Q:
        return Q()


def combinar(especificaciones) -> ConsultaSpecification:
    """Une con AND todas las specifications recibidas."""
    return reduce(lambda a, b: a & b, especificaciones, TodoSpecification())


# ---------------------------------------------------------------- Donacion

class DonacionPorEstadoSpecification(ConsultaSpecification):
    def __init__(self, estado: str):
        self.estado = estado

    def a_q(self) -> Q:
        return Q(estado=self.estado)


class DonacionPorCategoriaSpecification(ConsultaSpecification):
    def __init__(self, id_categoria: int):
        self.id_categoria = id_categoria

    def a_q(self) -> Q:
        return Q(categoria_id=self.id_categoria)


class DonacionPorDonanteSpecification(ConsultaSpecification):
    def __init__(self, id_organizacion: int):
        self.id_organizacion = id_organizacion

    def a_q(self) -> Q:
        return Q(organizacion_donante_id=self.id_organizacion)


class DonacionPorVencerSpecification(ConsultaSpecification):
    """
    Filtro de negocio: donaciones DISPONIBLES cuya fecha limite de
    retiro cae entre hoy y dentro de `dias` dias.
    """

    def __init__(self, dias: int, hoy=None):
        self.dias = dias
        self.hoy = hoy

    def a_q(self) -> Q:
        hoy = self.hoy or timezone.localdate()
        return Q(
            estado=Donacion.Estado.DISPONIBLE,
            fecha_limite_retiro__gte=hoy,
            fecha_limite_retiro__lte=hoy + timedelta(days=self.dias),
        )


# --------------------------------------------------------------- Solicitud

class SolicitudPorEstadoSpecification(ConsultaSpecification):
    def __init__(self, estado: str):
        self.estado = estado

    def a_q(self) -> Q:
        return Q(estado=self.estado)


class SolicitudDeOrganizacionSpecification(ConsultaSpecification):
    """Solicitudes realizadas por una organizacion beneficiaria."""

    def __init__(self, id_organizacion: int):
        self.id_organizacion = id_organizacion

    def a_q(self) -> Q:
        return Q(organizacion_beneficiaria_id=self.id_organizacion)


class SolicitudDeDonacionSpecification(ConsultaSpecification):
    """Solicitudes recibidas por una donacion."""

    def __init__(self, id_donacion: int):
        self.id_donacion = id_donacion

    def a_q(self) -> Q:
        return Q(donacion_id=self.id_donacion)