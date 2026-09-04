from ..models import Usuario
from .base_repository import BaseRepository


class UsuarioRepository(BaseRepository):

    model = Usuario

    def obtener_por_correo(self, correo):
        return self.model.objects.filter(
            correo=correo
        ).first()