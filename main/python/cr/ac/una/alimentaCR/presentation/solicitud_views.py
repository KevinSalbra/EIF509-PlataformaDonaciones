from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.exceptions import (
    DonacionNoDisponibleError,
    SolicitudNoExisteError,
    SolicitudNoPendienteError,
    UsuarioNoAutorizadoError,
)
from cr.ac.una.alimentaCR.business.services import SolicitudService

from .serializers import AceptarSolicitudRequestSerializer, EntregaResponseSerializer


class AceptarSolicitudView(APIView):
    """
    POST /api/solicitudes/<id_solicitud>/aceptar

    Body: {"id_usuario": <int>}

    Expone el Proceso #1 (aceptar una Solicitud y generar la Entrega)
    como endpoint REST. La vista solo se encarga de: validar el
    formato de entrada (DTO), invocar al servicio de negocio, traducir
    cada excepcion de negocio a un codigo HTTP, y serializar la
    respuesta (DTO de salida). Ninguna regla de negocio vive aqui.
    """

    def post(self, request, id_solicitud: int):
        request_serializer = AceptarSolicitudRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        id_usuario = request_serializer.validated_data["id_usuario"]

        try:
            entrega = SolicitudService().aceptar_solicitud(id_solicitud, id_usuario)
        except SolicitudNoExisteError as error:
            return Response({"detail": str(error)}, status=status.HTTP_404_NOT_FOUND)
        except UsuarioNoAutorizadoError as error:
            return Response({"detail": str(error)}, status=status.HTTP_403_FORBIDDEN)
        except (SolicitudNoPendienteError, DonacionNoDisponibleError) as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)

        response_serializer = EntregaResponseSerializer(entrega)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)