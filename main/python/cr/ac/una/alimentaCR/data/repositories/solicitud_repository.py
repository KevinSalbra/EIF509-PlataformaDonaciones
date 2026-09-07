from ..models import Solicitud
from .base_repository import BaseRepository
 
 
class SolicitudRepository(BaseRepository):
 
    model = Solicitud
 
    def obtener_por_donacion(self, donacion_id):
        return self.model.objects.filter(
            donacion_id=donacion_id
        )
 
    def obtener_por_organizacion_beneficiaria(
        self,
        organizacion_id
    ):
        return self.model.objects.filter(
            organizacion_beneficiaria_id=organizacion_id
        )
 
    def obtener_pendientes(self):
        return self.model.objects.filter(
            estado=Solicitud.Estado.PENDIENTE
        )
 
    def obtener_pendientes_por_donacion(self, donacion_id):
        return self.model.objects.filter(
            donacion_id=donacion_id,
            estado=Solicitud.Estado.PENDIENTE,
        )
 
    def obtener_pendientes_por_organizacion(self, organizacion_id):
        return self.model.objects.filter(
            organizacion_beneficiaria_id=organizacion_id,
            estado=Solicitud.Estado.PENDIENTE,
        )
 
    def existe_solicitud_pendiente(self, donacion_id, organizacion_id):
        return self.model.objects.filter(
            donacion_id=donacion_id,
            organizacion_beneficiaria_id=organizacion_id,
            estado=Solicitud.Estado.PENDIENTE,
        ).exists()
 