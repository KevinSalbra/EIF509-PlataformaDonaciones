from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import SolicitudService

from .serializers import AceptarSolicitudRequestSerializer, EntregaResponseSerializer


class AceptarSolicitudView(APIView):
    """
    POST /api/v1/solicitudes/<id_solicitud>/aceptar

    Body: {"id_usuario": <int>}

    Valida el formato (DTO), delega en el servicio y serializa la
    respuesta. Las excepciones de negocio las traduce el manejador
    global (presentation/exception_handler.py).
    """

    def post(self, request, id_solicitud: int):
        entrada = AceptarSolicitudRequestSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        entrega = SolicitudService().aceptar_solicitud(
            id_solicitud, entrada.validated_data["id_usuario"]
        )

        return Response(
            EntregaResponseSerializer(entrega).data,
            status=status.HTTP_201_CREATED,
        )