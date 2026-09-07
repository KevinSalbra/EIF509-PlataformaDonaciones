from ..models import Donacion
from .base_repository import BaseRepository
 
 
class DonacionRepository(BaseRepository):
 
    model = Donacion
 
    def obtener_disponibles(self):
        return self.model.objects.filter(
            estado=Donacion.Estado.DISPONIBLE
        )
 
    def obtener_por_organizacion_donante(self, organizacion_id):
        return self.model.objects.filter(
            organizacion_donante_id=organizacion_id
        )
 
    def obtener_por_categoria(self, categoria_id):
        return self.model.objects.filter(
            categoria_id=categoria_id
        )
 
    def obtener_disponibles_por_categoria(self, categoria_id):
        return self.model.objects.filter(
            estado=Donacion.Estado.DISPONIBLE,
            categoria_id=categoria_id,
        )
 
    def obtener_proximas_a_vencer(self, fecha_limite):
        return self.model.objects.filter(
            estado=Donacion.Estado.DISPONIBLE,
            fecha_limite_retiro__lte=fecha_limite,
        )