from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import DonacionService

from .serializers import (
    DonacionResponseSerializer,
    PublicarDonacionRequestSerializer,
)


class PublicarDonacionView(APIView):
    """
    POST /api/v1/donaciones/publicar

    Expone el Proceso 1 (publicar una Donacion). Valida el formato
    con el DTO, delega en DonacionService y serializa la respuesta.
    Las excepciones de negocio las traduce el manejador global.
    """

    def post(self, request):
        entrada = PublicarDonacionRequestSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        donacion = DonacionService().publicar_donacion(
            id_organizacion=datos["id_organizacion"],
            id_categoria=datos["id_categoria"],
            alimento=datos["alimento"],
            descripcion=datos.get("descripcion"),
            cantidad=datos["cantidad"],
            unidad_medida=datos["unidad_medida"],
            fecha_limite_retiro=datos["fecha_limite_retiro"],
        )

        return Response(
            DonacionResponseSerializer(donacion).data,
            status=status.HTTP_201_CREATED,
        )