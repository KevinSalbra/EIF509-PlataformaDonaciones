from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import EntregaService

from .entrega_serializers import (
    CoordinarEntregaRequestSerializer,
    EntregaResponseSerializer,
)


class EntregaListaView(APIView):
    """
    GET /api/v1/entregas -> 200, lista de entregas

    Las entregas no se crean por POST: las genera el proceso de aceptar
    una solicitud (POST /api/v1/solicitudes/<id>/aceptar).
    """

    def get(self, request):
        entregas = EntregaService().listar_entregas()
        return Response(EntregaResponseSerializer(entregas, many=True).data)


class EntregaDetalleView(APIView):
    """
    GET   /api/v1/entregas/<id> -> 200 | 404
    PATCH /api/v1/entregas/<id> -> 200 | 400, 403, 404, 409, 422

    El PATCH expone el Proceso 5: coordinar la entrega (fecha acordada,
    lugar y observaciones). Solo se modifican los campos enviados.
    """

    def get(self, request, id_entrega: int):
        entrega = EntregaService().obtener_entrega(id_entrega)
        return Response(EntregaResponseSerializer(entrega).data)

    def patch(self, request, id_entrega: int):
        entrada = CoordinarEntregaRequestSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        cambios = dict(entrada.validated_data)
        id_usuario = cambios.pop("id_usuario")

        entrega = EntregaService().coordinar_entrega(
            id_entrega, id_usuario, cambios
        )
        return Response(EntregaResponseSerializer(entrega).data)