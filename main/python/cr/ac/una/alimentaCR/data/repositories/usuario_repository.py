from ..models import Usuario
from .base_repository import BaseRepository
 
 
class UsuarioRepository(BaseRepository):
 
    model = Usuario
 
    def obtener_por_correo(self, correo):
        return self.model.objects.filter(
            correo=correo
        ).first()
 
    def obtener_por_organizacion(self, organizacion_id):
        return self.model.objects.filter(
            organizacion_id=organizacion_id
        )
 
    def obtener_activos(self):
        return self.model.objects.filter(
            estado=Usuario.Estado.ACTIVO
        )
 