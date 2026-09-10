from ..models import Entrega
from .base_repository import BaseRepository
 
 
class EntregaRepository(BaseRepository):
 
    model = Entrega
 
    def obtener_por_solicitud(self, solicitud_id):
        return self.model.objects.filter(
            solicitud_id=solicitud_id
        ).first()
 
    def obtener_por_estado(self, estado):
        return self.model.objects.filter(
            estado=estado
        )
 
    def obtener_pendientes(self):
        return self.model.objects.filter(
            estado=Entrega.Estado.PENDIENTE
        ).order_by("fecha_acordada")