from ..models import Organizacion
from .base_repository import BaseRepository


class OrganizacionRepository(BaseRepository):
    model = Organizacion

    def obtener_por_tipo(self, tipo):
        return self.model.objects.filter(tipo=tipo)

    def obtener_aprobadas(self):
        return self.model.objects.filter(
            estado=Organizacion.Estado.APROBADA
        )

    def obtener_por_cedula_juridica(self, cedula_juridica):
        return self.model.objects.filter(
            cedula_juridica=cedula_juridica
        ).first()