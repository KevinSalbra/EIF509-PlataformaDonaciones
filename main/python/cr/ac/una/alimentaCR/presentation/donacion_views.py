from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import DonacionService

from .listados import (
    DonacionConsultaSerializer,
    listar_paginado,
    respuesta_paginada,
)
from .permisos import EsRepresentanteDonante
from .serializers import (
    DonacionResponseSerializer,
    PublicarDonacionRequestSerializer,
)


class DonacionListaView(APIView):
    """
    GET /api/v1/donaciones -> 200, lista de donaciones
    """

    @extend_schema(
        operation_id="listar_donaciones",
        summary="Listar donaciones",
        description=(
            "Obtiene la lista de donaciones aplicando los filtros, "
            "ordenamiento y parametros de consulta disponibles."
        ),
        parameters=[DonacionConsultaSerializer],
        responses={
            200: respuesta_paginada(
                "DonacionPaginadaResponse",
                DonacionResponseSerializer,
            ),
        },
        auth=[],
    )
    def get(self, request):
        consulta = DonacionConsultaSerializer(
            data=request.query_params
        )
        consulta.is_valid(raise_exception=True)
        datos = consulta.validated_data

        coleccion = DonacionService().listar(
            estado=datos.get("estado"),
            id_categoria=datos.get("id_categoria"),
            id_organizacion=datos.get("id_organizacion"),
            por_vencer_en_dias=datos.get("por_vencer_en_dias"),
            orden=consulta.orden(),
        )

        return listar_paginado(
            request,
            coleccion,
            DonacionResponseSerializer,
        )


class DonacionDetalleView(APIView):
    """
    GET /api/v1/donaciones/<id> -> 200 | 404
    """

    @extend_schema(
        operation_id="obtener_donacion",
        summary="Obtener donacion",
        description=(
            "Obtiene una donacion mediante su identificador."
        ),
        responses={200: DonacionResponseSerializer},
        auth=[],
    )
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

    permission_classes = [EsRepresentanteDonante]

    @extend_schema(
        operation_id="publicar_donacion",
        summary="Publicar donacion",
        description=(
            "Publica una nueva donacion para la organizacion "
            "donante del usuario autenticado."
        ),
        request=PublicarDonacionRequestSerializer,
        responses={201: DonacionResponseSerializer},
    )
    def post(self, request):
        entrada = PublicarDonacionRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        donacion = DonacionService().publicar_donacion(
            id_organizacion=request.user.organizacion_id,
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