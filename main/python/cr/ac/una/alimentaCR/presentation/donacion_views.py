from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import DonacionService

from .serializers import (
    DonacionResponseSerializer,
    PublicarDonacionRequestSerializer,
)

from .listados import DonacionConsultaSerializer, listar_paginado

class DonacionListaView(APIView):
    """
    GET /api/v1/donaciones -> 200, lista de donaciones
    """

    def get(self, request):
        consulta = DonacionConsultaSerializer(data=request.query_params)
        consulta.is_valid(raise_exception=True)
        datos = consulta.validated_data
        coleccion = DonacionService().listar(
            estado=datos.get("estado"),
            id_categoria=datos.get("id_categoria"),
            id_organizacion=datos.get("id_organizacion"),
            por_vencer_en_dias=datos.get("por_vencer_en_dias"),
            orden=consulta.orden(),
        )
        return listar_paginado(request, coleccion, DonacionResponseSerializer)

class DonacionDetalleView(APIView):
    """
    GET /api/v1/donaciones/<id> -> 200 | 404
    """

    def get(self, request, id_donacion: int):
        donacion = DonacionService().obtener(
            id_donacion
        )

        return Response(
            DonacionResponseSerializer(donacion).data
        )


class PublicarDonacionView(APIView):
    """
    POST /api/v1/donaciones/publicar -> 201 + Location | 400

    Expone el proceso de publicar una Donacion. Valida el formato
    con el DTO, delega en DonacionService y serializa la respuesta.
    Las excepciones de negocio las traduce el manejador global.
    """

    def post(self, request):
        entrada = PublicarDonacionRequestSerializer(
            data=request.data
        )
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

        respuesta = Response(
            DonacionResponseSerializer(donacion).data,
            status=status.HTTP_201_CREATED,
        )

        respuesta["Location"] = request.build_absolute_uri(
            reverse(
                "donacion_detalle",
                args=[donacion.id_donacion],
            )
        )

        return respuesta