from ..models import Entrega
from .base_repository import BaseRepository
from django.db.models import Q
 
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
    
    def visibles_para_organizacion(self, organizacion_id):
        """
        Entregas en las que participa la organizacion: la beneficiaria
        de la solicitud aceptada o la donante de la donacion.
        """
        return self.model.objects.filter(
            Q(solicitud__organizacion_beneficiaria_id=organizacion_id)
            | Q(solicitud__donacion__organizacion_donante_id=organizacion_id)
        )