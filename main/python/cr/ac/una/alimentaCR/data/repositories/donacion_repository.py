from ..models import Donacion
from .base_repository import BaseRepository


class DonacionRepository(BaseRepository):

    model = Donacion

    def obtener_disponibles(self):
        return self.model.objects.filter(
            estado=Donacion.Estado.DISPONIBLE
        )

    def filtrar_donaciones(
        self,
        estado=None,
        categoria_id=None,
        organizacion_id=None,
        fecha_limite=None
    ):
        queryset = self.model.objects.all()

        if estado is not None:
            queryset = queryset.filter(
                estado=estado
            )

        if categoria_id is not None:
            queryset = queryset.filter(
                categoria_id=categoria_id
            )

        if organizacion_id is not None:
            queryset = queryset.filter(
                organizacion_donante_id=organizacion_id
            )

        if fecha_limite is not None:
            queryset = queryset.filter(
                fecha_limite_retiro__lte=fecha_limite
            )

        return queryset