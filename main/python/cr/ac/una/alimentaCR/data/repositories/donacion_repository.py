from ..models import Donacion
from .base_repository import BaseRepository


class DonacionRepository(BaseRepository):

    model = Donacion

    def obtener_disponibles(self):
        return self.model.objects.filter(
            estado=Donacion.Estado.DISPONIBLE
        )