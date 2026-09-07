from ..models import Categoria
from .base_repository import BaseRepository


class CategoriaRepository(BaseRepository):

    model = Categoria
    
    def obtener_activas(self):
        return self.model.objects.filter(
            estado=Categoria.Estado.ACTIVA
        )