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

    def existe_solicitud_pendiente(self, donacion_id, organizacion_id):
        return self.model.objects.filter(
            donacion_id=donacion_id,
            organizacion_beneficiaria_id=organizacion_id,
            estado=Solicitud.Estado.PENDIENTE,
        ).exists()

    def filtrar_solicitudes(
        self,
        estado=None,
        donacion_id=None,
        organizacion_id=None
    ):
        queryset = self.model.objects.all()

        if estado is not None:
            queryset = queryset.filter(
                estado=estado
            )

        if donacion_id is not None:
            queryset = queryset.filter(
                donacion_id=donacion_id
            )

        if organizacion_id is not None:
            queryset = queryset.filter(
                organizacion_beneficiaria_id=organizacion_id
            )

        return queryset