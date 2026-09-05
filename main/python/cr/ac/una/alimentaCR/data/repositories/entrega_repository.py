from ..models import Entrega
from .base_repository import BaseRepository


class EntregaRepository(BaseRepository):

    model = Entrega

    def obtener_por_solicitud(self, solicitud_id):
        return self.model.objects.filter(
            solicitud_id=solicitud_id
        ).first()