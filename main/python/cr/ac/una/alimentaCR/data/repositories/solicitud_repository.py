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